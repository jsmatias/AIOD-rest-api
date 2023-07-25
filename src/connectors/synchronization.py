from typing import Dict, List
import argparse
from sqlmodel import SQLModel
from config import DB_CONFIG
from connectors.record_error import RecordError
from connectors.resource_with_relations import ResourceWithRelations
from database.model.platform.platform_names import PlatformName
from datetime import datetime
from connectors.abstract.resource_connector import ResourceConnector
from connectors.abstract.resource_connector_by_date import ResourceConnectorByDate
from connectors.abstract.resource_connector_by_id import ResourceConnectorById
from connectors.huggingface.huggingface_dataset_connector import HuggingFaceDatasetConnector
from connectors.openml.openml_dataset_connector import OpenMlDatasetConnector
from connectors.zenodo.zenodo_dataset_connector import ZenodoDatasetConnector
from database.setup import (
    connect_to_database,
)
from sqlalchemy.engine import Engine


class Synchronization:
    dataset_connectors = {
        c.platform_name: c
        for c in (
            OpenMlDatasetConnector(),
            HuggingFaceDatasetConnector(),
            ZenodoDatasetConnector(),
        )
    }

    def _parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Please refer to the README.")
        parser.add_argument(
            "--populate-datasets",
            default=[],
            nargs="+",
            choices=[p.name for p in PlatformName],
            help="Zero,     one or more platforms with which the datasets should get populated.",
        )
        return parser.parse_args()

    def _connector_from_platform_name(
        self, connector_type: str, connector_dict: Dict, platform_name: str
    ):
        """Get the connector from the connector_dict, identified by its platform name."""
        try:
            platform = PlatformName(platform_name)
        except ValueError:
            raise ValueError(
                f"platform " f"'{platform_name}' not recognized.",
            )
        connector = connector_dict.get(platform, None)
        if connector is None:
            possibilities = ", ".join(f"`{c}`" for c in self.dataset_connectors.keys())
            msg = (
                f"No {connector_type} connector for platform '{platform_name}' available. Possible "
                f"values: {possibilities}"
            )
            raise ValueError(msg)
        return connector

    def _engine(self, rebuild_db: str) -> Engine:
        """
        Return a SqlAlchemy engine, backed by the MySql connection as
        configured in the configuration file.
        """
        username = DB_CONFIG.get("name", "root")
        password = DB_CONFIG.get("password", "ok")
        host = DB_CONFIG.get("host", "demodb")
        port = DB_CONFIG.get("port", 3306)
        database = DB_CONFIG.get("database", "aiod")

        db_url = f"mysql://{username}:{password}@{host}:{port}/{database}"

        delete_before_create = rebuild_db == "always"
        return connect_to_database(db_url, delete_first=delete_before_create)

    def store_records(
        self, engine: Engine, items: List["SQLModel" | "ResourceWithRelations[SQLModel]"]
    ):
        """
        This function store on the database all the items using the engine
        """
        pass

    def start(self):
        args = self._parse_args()
        dataset_connectors: List["ResourceConnector"] = [
            self._connector_from_platform_name("dataset", self.dataset_connectors, platform_name)
            for platform_name in args.populate_datasets
        ]
        # add all dict connectors
        connectors_ = dataset_connectors
        engine = self._engine(args.rebuild_db)

        # init the database with all connectors
        for connector in connectors_:
            if isinstance(connector, HuggingFaceDatasetConnector):
                records = connector.fetch_all()
                self.store_records(engine, records)

            elif isinstance(connector, ResourceConnectorByDate):
                records = []
                items = connector.fetch(datetime.min, datetime.max)
                for item in items:
                    if isinstance(item, RecordError):
                        # handle error
                        pass
                    else:
                        records.append(item)
                self.store_records(engine, records)

            elif isinstance(connector, ResourceConnectorById):
                # Retrieve all records
                from_id = 0
                to_id = from_id + 10
                finished = False
                records: List["SQLModel" | "ResourceWithRelations[SQLModel]"] = []
                while not finished:
                    items = connector.fetch(from_id, to_id)
                    if records[0].error == "No more datasets to retrieve":
                        finished = True
                    else:
                        from_id += 10
                        to_id = from_id + 10
                for item in items:
                    if isinstance(item, RecordError):
                        # handle error
                        pass
                    else:
                        records.append(item)
                self.store_records(engine, records)

            else:
                pass  # "Unknown connector type!
