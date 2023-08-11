from database.model.new.agent.organisation import Organisation
from routers.resource_router import ResourceRouter


class OrganisationRouter(ResourceRouter):
    @property
    def version(self) -> int:
        return 0

    @property
    def resource_name(self) -> str:
        return "organisation"

    @property
    def resource_name_plural(self) -> str:
        return "organisations"

    @property
    def resource_class(self) -> type[Organisation]:
        return Organisation
