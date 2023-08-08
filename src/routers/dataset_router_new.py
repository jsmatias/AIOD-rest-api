from database.model.new.dataset.dataset import DatasetNew

from routers.resource_router import ResourceRouter


class DatasetRouterNew(ResourceRouter):
    @property
    def version(self) -> int:
        return 0

    @property
    def resource_name(self) -> str:
        return "dataset_new"

    @property
    def resource_name_plural(self) -> str:
        return "datasets_new"

    @property
    def resource_class(self) -> type[DatasetNew]:
        return DatasetNew
