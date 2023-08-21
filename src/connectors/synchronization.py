import argparse
import importlib
import json
import logging
import pathlib
import sys
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Session

import routers
from connectors.abstract.resource_connector import ResourceConnector
from connectors.record_error import RecordError
from connectors.resource_with_relations import ResourceWithRelations
from database.setup import _create_or_fetch_related_objects, _get_existing_resource, sqlmodel_engine
from routers import ResourceRouter

RELATIVE_PATH_LOG = pathlib.Path("connector.log")
RELATIVE_PATH_STATE_JSON = pathlib.Path("state.json")
RELATIVE_PATH_ERROR_CSV = pathlib.Path("errors.csv")


def _parse_args() -> argparse.Namespace:
    # TODO: write readme
    parser = argparse.ArgumentParser(description="Please refer to the README.")
    parser.add_argument(
        "--connector",
        required=True,
        help="The connector to use. Please provide a relative path such as "
        "'connectors.zenodo.zenodo_dataset_connector.ZenodoDatasetConnector' where the "
        "last part is the class name.",
    )
    parser.add_argument(
        "--working-dir",
        required=True,
        help="The working directory. The status will be stored here, next to the logs and a "
        "list of failed resources",
    )
    parser.add_argument(
        "--from-date",
        type=lambda d: datetime.strptime(d, "%Y-%m-%d").date(),
        help="The start date. Only relevant for the first run of date-based connectors. "
        "In subsequent runs, date-based connectors will synchronize from the previous "
        "end-time. Format: YYYY-MM-DD",
    )
    parser.add_argument(
        "--from-identifier",
        type=str,
        help="The start identifier. Only relevant for the first run of identifier-based "
        "connectors. In subsequent runs, identifier-based connectors will "
        "synchronize from the previous end-identifier.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Implemented by some connectors for testing purposes: limit the number of results.",
    )
    parser.add_argument(
        "--save_every",
        type=int,
        help="Save the state file every N records. In case that the complete program is killed, "
        "you can then resume the next run from the last saved state.",
    )
    return parser.parse_args()


def exception_handler(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def save_to_database(
    session: Session,
    connector: ResourceConnector,
    router: ResourceRouter,
    item: SQLModel | ResourceWithRelations[SQLModel] | RecordError,
) -> Optional[RecordError]:
    if isinstance(item, RecordError):
        return item
    try:
        if isinstance(item, ResourceWithRelations):
            resource_create_instance = item.resource
            _create_or_fetch_related_objects(session, item)
        else:
            resource_create_instance = item
        existing = _get_existing_resource(
            session, resource_create_instance, connector.resource_class
        )
        if existing is None:  # TODO: if not None, update
            router.create_resource(session, resource_create_instance)

    except Exception as e:
        return RecordError(identifier=str(item.identifier), error=e)  # type:ignore
    session.flush()
    return None


def main():
    args = _parse_args()
    working_dir = pathlib.Path(args.working_dir)
    working_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=working_dir / RELATIVE_PATH_LOG, encoding="utf-8", level=logging.INFO
    )
    logging.getLogger().addHandler(logging.StreamHandler())
    sys.excepthook = exception_handler

    module_path = ".".join(args.connector.split(".")[0:-1])
    connector_cls_name = args.connector.split(".")[-1]
    module = importlib.import_module(module_path)
    connector: ResourceConnector = getattr(module, connector_cls_name)()

    error_path = working_dir / RELATIVE_PATH_ERROR_CSV
    state_path = working_dir / RELATIVE_PATH_STATE_JSON
    error_path.parents[0].mkdir(parents=True, exist_ok=True)
    state_path.parents[0].mkdir(parents=True, exist_ok=True)
    first_run = not state_path.exists()
    if not first_run:
        with open(state_path, "r") as f:
            state = json.load(f)
    else:
        state = {}

    items = connector.run(
        state=state,
        from_identifier=args.from_identifier,
        from_date=args.from_date,
        limit=args.limit,
    )

    (router,) = [
        router
        for router in routers.resource_routers
        if router.resource_class == connector.resource_class
    ]

    engine = sqlmodel_engine(rebuild_db="never")

    with Session(engine) as session:
        for i, item in enumerate(items):
            error = save_to_database(router=router, connector=connector, session=session, item=item)
            if error:
                if isinstance(error.error, str):
                    logging.error(f"Error on identifier {error.identifier}: {error.error}")
                else:
                    logging.error(f"Error on identifier {error.identifier}", exc_info=error.error)
                with open(error_path, "a") as f:
                    error_cleaned = "".join(
                        c if c.isalnum() or c == "" else "_" for c in str(error.error)
                    )
                    f.write(f'"{error.identifier}","{error_cleaned}"\n')
            if args.save_every and i > 0 and i % args.save_every == 0:
                logging.debug(f"Saving state after handling record {i}")
                with open(state_path, "w") as f:
                    json.dump(state, f, indent=4)
                session.commit()
    with open(state_path, "w") as f:
        session.commit()
        json.dump(state, f, indent=4)
    logging.info("Done")


if __name__ == "__main__":
    main()
