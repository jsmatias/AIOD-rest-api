from database.model.case_study.case_study import CaseStudy
from routers.search_router import SearchRouter


class SearchRouterCaseStudies(SearchRouter[CaseStudy]):
    @property
    def es_index(self) -> str:
        return "case_study"

    @property
    def resource_name_plural(self) -> str:
        return "case_studies"

    @property
    def resource_class(self):
        return CaseStudy

    @property
    def linked_fields(self) -> set[str]:
        return {
            "alternate_name",
            "application_area",
            "industrial_sector",
            "research_area",
            "scientific_domain",
        }
