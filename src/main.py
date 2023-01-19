"""
Defines Rest API endpoints.

Note: order matters for overloaded paths
(https://fastapi.tiangolo.com/tutorial/path-params/#order-matters).
"""
import argparse
import tomllib
import traceback
from dataclasses import asdict

import uvicorn
from fastapi import Query, Body, Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import select, Engine, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import connectors
from connectors import Platform
from database.models import Dataset, Publication
from database.setup import connect_to_database, populate_database


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Please refer to the README.")
    parser.add_argument(
        "--rebuild-db",
        default="only-if-empty",
        choices=["no", "only-if-empty", "always"],
        help="Determines if the database is recreated.",
    )
    parser.add_argument(
        "--populate-datasets",
        default="example",
        choices=["nothing"] + [p.name for p in Platform],
        help="Determines if the database gets populated with datasets.",
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
    with open("config.toml", "rb") as fh:
        config = tomllib.load(fh)
    db_config = config.get("database", {})
    username = db_config.get("name", "root")
    password = db_config.get("password", "ok")
    host = db_config.get("host", "demodb")
    port = db_config.get("port", 3306)
    database = db_config.get("database", "aiod")

    db_url = f"mysql://{username}:{password}@{host}:{port}/{database}"

    delete_before_create = rebuild_db == "always"
    return connect_to_database(db_url, delete_first=delete_before_create)


def _wrap_as_http_exception(exception: Exception) -> HTTPException:
    if isinstance(exception, HTTPException):
        return exception

    # This is an unexpected error. A mistake on our part. End users should not be informed about
    # details of problems they are not expected to fix, so we give a generic response and log the
    # error.
    traceback.print_exc()
    return HTTPException(
        status_code=500,
        detail=(
            "Unexpected exception while processing your request. Please contact the maintainers."
        ),
    )


def add_routes(app: FastAPI, engine: Engine):
    """Add routes to the FastAPI application"""

    @app.get("/", response_class=HTMLResponse)
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

    # Multiple endpoints share the same set of parameters, we define a class for easy re-use of
    # dependencies:
    # https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/?h=depends#classes-as-dependencies # noqa
    class Pagination(BaseModel):
        offset: int = 0
        limit: int = 100

    @app.get("/datasets/")
    def list_datasets(
        platforms: list[str] | None = Query(default=[]),
        pagination: Pagination = Depends(Pagination),
    ) -> list[dict]:
        """Lists all datasets registered with AIoD.

        Query Parameter
        ------
         * platforms, list[str], optional: if provided, list only datasets from the given platform.
        """
        # For additional information on querying through SQLAlchemy's ORM:
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
        try:
            platform_filter = Dataset.platform.in_(platforms) if platforms else True
            with Session(engine) as session:
                return [
                    dataset.to_dict(depth=0)
                    for dataset in session.scalars(
                        select(Dataset)
                        .where(platform_filter)
                        .offset(pagination.offset)
                        .limit(pagination.limit)
                    ).all()
                ]
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.get("/dataset/{platform}/{identifier}")
    def get_dataset(platform: str, identifier: str) -> dict:
        """Retrieve all meta-data for a specific dataset."""
        try:
            with Session(engine) as session:
                query = select(Dataset).where(
                    and_(
                        Dataset.platform_specific_identifier == identifier,
                        Dataset.platform == platform,
                    )
                )
                dataset = session.scalars(query).first()
                if not dataset:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Dataset '{identifier}' of '{platform}' not found "
                        "in the database.",
                    )
                connector = connectors.dataset_connectors.get(dataset.platform.lower(), None)
                if connector is not None:
                    dataset_meta = connector.fetch(dataset)
                else:
                    raise HTTPException(
                        status_code=501,
                        detail=f"No connector for platform '{platform}' available.",
                    )

                return {
                    **asdict(
                        dataset_meta, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
                    ),
                    **dataset.to_dict(depth=1),
                }
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.post("/register/dataset/")
    def register_dataset(
        name: str = Body(min_length=1, max_length=50),
        platform: str = Body(min_length=1, max_length=30),
        platform_identifier: str = Body(min_length=1, max_length=100),
    ) -> dict:
        """Register a dataset with AIoD.

        Expects a JSON body with the following key/values:
         - name (max 150 characters): Name of the dataset.
         - platform (max 30 characters): Name of the platform on which the dataset resides.
         - platform_identifier (max 100 characters):
            Identifier which uniquely defines the dataset for the platform.
            For example, with OpenML that is the dataset id.
        """
        # Alternatively, consider defining Pydantic models instead to define the request body:
        # https://fastapi.tiangolo.com/tutorial/body/#request-body
        try:
            with Session(engine) as session:
                new_dataset = Dataset(
                    name=name, platform=platform, platform_specific_identifier=platform_identifier
                )
                session.add(new_dataset)
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    query = select(Dataset).where(
                        and_(Dataset.platform == platform, Dataset.name == name)
                    )
                    existing_dataset = session.scalars(query).first()
                    raise HTTPException(
                        status_code=409,
                        detail="There already exists a dataset with the same "
                        f"platform and name, with id={existing_dataset.id}.",
                    )
                return new_dataset.to_dict(depth=1)
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.get("/publications")
    def list_publications(pagination: Pagination = Depends(Pagination)) -> list[dict]:
        """Lists all publications registered with AIoD."""
        try:
            with Session(engine) as session:
                return [
                    publication.to_dict(depth=0)
                    for publication in session.scalars(
                        select(Publication).offset(pagination.offset).limit(pagination.limit)
                    ).all()
                ]
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.get("/publication/{identifier}")
    def get_publication(identifier: str) -> dict:
        """Retrieves all information for a specific publication registered with AIoD."""
        try:
            with Session(engine) as session:
                query = select(Publication).where(Publication.id == identifier)
                publication = session.scalars(query).first()
                if not publication:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Publication '{identifier}' not found in the database.",
                    )
                return publication.to_dict(depth=1)
        except Exception as e:
            raise _wrap_as_http_exception(e)


def create_app() -> FastAPI:
    """Create the FastAPI application, complete with routes."""
    app = FastAPI()
    args = _parse_args()
    engine = _engine(args.rebuild_db)
    if args.populate in ["example", "openml"]:
        populate_database(
            engine,
            platform_data=args.populate.lower(),
            platform_publications="example",
            only_if_empty=True,
        )
    add_routes(app, engine)
    return app


def main():
    """Run the application. Placed in a separate function, to avoid having global variables"""
    args = _parse_args()
    uvicorn.run("main:create_app", host="0.0.0.0", reload=args.reload, factory=True)


if __name__ == "__main__":
    main()
