from typing import Type

from converters import dataset_converter_instance
from converters.orm_converters.orm_converter import OrmConverter
from converters.schema.dcat import DcatApWrapper
from converters.schema.schema_dot_org import SchemaDotOrgDataset
from converters.schema_converters import (
    dataset_converter_schema_dot_org_instance,
    dataset_converter_dcatap_instance,
)
from converters.schema_converters.schema_converter import SchemaConverter
from database.model.dataset import OrmDataset
from routers.resource_router import ResourceRouter
from schemas import AIoDDataset


class DatasetRouter(ResourceRouter[OrmDataset, AIoDDataset]):
    @property
    def version(self) -> int:
        return 0

    @property
    def resource_name(self) -> str:
        return "dataset"

    @property
    def resource_name_plural(self) -> str:
        return "datasets"

    @property
    def aiod_class(self) -> Type[AIoDDataset]:
        return AIoDDataset

    @property
    def orm_class(self) -> Type[OrmDataset]:
        return OrmDataset

    @property
    def converter(self) -> OrmConverter[AIoDDataset, OrmDataset]:
        return dataset_converter_instance

    @property
    def schema_converters(
        self,
    ) -> dict[str, SchemaConverter[AIoDDataset, SchemaDotOrgDataset | DcatApWrapper]]:
        return {
            "schema.org": dataset_converter_schema_dot_org_instance,
            "dcat-ap": dataset_converter_dcatap_instance,
        }