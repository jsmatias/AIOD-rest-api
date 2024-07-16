from database.model.service.service import Service
from routers.search_router import SearchRouter


class SearchRouterServices(SearchRouter[Service]):
    @property
    def es_index(self) -> str:
        return "service"

    @property
    def resource_name_plural(self) -> str:
        return "services"

    @property
    def resource_class(self):
        return Service

    @property
    def indexed_fields(self):
        return {"name", "description_plain", "description_html", "slogan"}
