"""
Defines Rest API endpoints.

Note: order matters for overloaded paths
(https://fastapi.tiangolo.com/tutorial/path-params/#order-matters).
"""
import argparse
import logging
from typing import Dict

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import Json
from sqlalchemy.engine import Engine
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_501_NOT_IMPLEMENTED

import connectors
import routers
from authentication import get_current_user
from config import DB_CONFIG, KEYCLOAK_CONFIG
from database.model.platform.platform_names import PlatformName
from database.setup import connect_to_database, populate_database


def _parse_args() -> argparse.Namespace:
    # TODO: refactor configuration (https://github.com/aiondemand/AIOD-rest-api/issues/82)
    parser = argparse.ArgumentParser(description="Please refer to the README.")
    parser.add_argument("--url-prefix", default="", help="Prefix for the api url.")
    parser.add_argument(
        "--rebuild-db",
        default="only-if-empty",
        choices=["no", "only-if-empty", "always"],
        help="Determines if the database is recreated.",
    )
    parser.add_argument(
        "--populate-datasets",
        default=[],
        nargs="+",
        choices=[p.name for p in PlatformName],
        help="Zero, one or more platforms with which the datasets should get populated.",
    )
    parser.add_argument(
        "--fill-with-examples",
        default=[],
        nargs="+",
        choices=connectors.example_connectors.keys(),
        help="Zero, one or more resources with which the database will have examples.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of initial resources with which the database is populated, "
        "per resource and per platform.",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Use `--reload` for FastAPI.",
    )
    return parser.parse_args()


def _engine(rebuild_db: str) -> Engine:
    """
    Return a SqlAlchemy engine, backed by the MySql connection as configured in the configuration
    file.
    """
    username = DB_CONFIG.get("name", "root")
    password = DB_CONFIG.get("password", "ok")
    host = DB_CONFIG.get("host", "demodb")
    port = DB_CONFIG.get("port", 3306)
    database = DB_CONFIG.get("database", "aiod")

    db_url = f"mysql://{username}:{password}@{host}:{port}/{database}"

    delete_before_create = rebuild_db == "always"
    return connect_to_database(db_url, delete_first=delete_before_create)


def _connector_from_platform_name(connector_type: str, connector_dict: Dict, platform_name: str):
    """Get the connector from the connector_dict, identified by its platform name."""
    try:
        platform = PlatformName(platform_name)
    except ValueError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"platform " f"'{platform_name}' not recognized.",
        )
    connector = connector_dict.get(platform, None)
    if connector is None:
        possibilities = ", ".join(f"`{c}`" for c in connectors.dataset_connectors.keys())
        msg = (
            f"No {connector_type} connector for platform '{platform_name}' available. Possible "
            f"values: {possibilities}"
        )
        raise HTTPException(status_code=HTTP_501_NOT_IMPLEMENTED, detail=msg)
    return connector


def _connector_example_from_resource(resource):
    connector_dict = connectors.example_connectors
    connector = connector_dict.get(resource, None)
    if connector is None:
        possibilities = ", ".join(f"`{c}`" for c in connectors.example_connectors.keys())
        msg = (
            f"No example connector for resource '{resource}' available. Possible "
            f"values: {possibilities}"
        )
        logging.warning(msg)
        raise HTTPException(status_code=HTTP_501_NOT_IMPLEMENTED, detail=msg)
    return connector


def add_routes(app: FastAPI, engine: Engine, url_prefix=""):
    """Add routes to the FastAPI application"""

    @app.get(url_prefix + "/", response_class=HTMLResponse)
    def home() -> str:
        """Provides a redirect page to the docs."""
        return """
        <!DOCTYPE html>
        <html>
          <head>
            <meta http-equiv="refresh" content="0; url='docs'" />
          </head>
          <body>
            <p>The REST API documentation is <a href="docs">here</a>.</p>
          </body>
        </html>
        """

    @app.get(url_prefix + "/authorization_test")
    def test_authorization(user: Json = Depends(get_current_user)) -> dict:
        """
        Returns the user, if authenticated correctly.
        """
        return {"msg": "success", "user": user}

    for router in routers.resource_routers + routers.other_routers:
        app.include_router(router.create(engine, url_prefix))


def create_app() -> FastAPI:
    """Create the FastAPI application, complete with routes."""
    args = _parse_args()
    app = FastAPI(
        openapi_url=f"{args.url_prefix}/openapi.json",
        docs_url=f"{args.url_prefix}/docs",
        swagger_ui_oauth2_redirect_url=f"{args.url_prefix}/docs/oauth2-redirect",
        swagger_ui_init_oauth={
            "clientId": KEYCLOAK_CONFIG.get("client_id_swagger"),
            "realm": KEYCLOAK_CONFIG.get("realm"),
            "appName": "AIoD Metadata Catalogue",
            "usePkceWithAuthorizationCodeGrant": True,
            "scopes": KEYCLOAK_CONFIG.get("scopes"),
        },
    )

    dataset_connectors = [
        _connector_from_platform_name("dataset", connectors.dataset_connectors, platform_name)
        for platform_name in args.populate_datasets
    ]

    examples_connectors = [
        _connector_example_from_resource(resource) for resource in args.fill_with_examples
    ]
    connectors_ = dataset_connectors + examples_connectors
    engine = _engine(args.rebuild_db)
    if len(connectors_) > 0:
        populate_database(
            engine,
            connectors=connectors_,
            only_if_empty=True,
            limit=args.limit,
        )

    add_routes(app, engine, url_prefix=args.url_prefix)
    return app


def main():
    """Run the application. Placed in a separate function, to avoid having global variables"""
    args = _parse_args()
    uvicorn.run("main:create_app", host="0.0.0.0", reload=args.reload, factory=True)


if __name__ == "__main__":
    main()
