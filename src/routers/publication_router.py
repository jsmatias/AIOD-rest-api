from database.model.new.publication.publication import PublicationNew
from routers.resource_router import ResourceRouter


class PublicationRouter(ResourceRouter):
    @property
    def version(self) -> int:
        return 0

    @property
    def resource_name(self) -> str:
        return "publication"

    @property
    def resource_name_plural(self) -> str:
        return "publications"

    @property
    def resource_class(self) -> type[PublicationNew]:
        return PublicationNew
