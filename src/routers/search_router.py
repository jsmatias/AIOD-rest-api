import abc
from typing import TypeVar, Generic, Any, Type, Literal, Annotated, TypeAlias

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pydantic.generics import GenericModel
from sqlmodel import SQLModel, select, Field
from starlette import status

from database.model.concept.aiod_entry import AIoDEntryRead
from database.model.concept.concept import AIoDConcept
from database.model.platform.platform import Platform
from database.model.resource_read_and_create import resource_read
from database.session import DbSession
from error_handling import as_http_exception
from .search_routers.elasticsearch import ElasticsearchSingleton

LIMIT_MAX = 1000

RESOURCE = TypeVar("RESOURCE", bound=AIoDConcept)
RESOURCE_READ = TypeVar("RESOURCE_READ", bound=BaseModel)


class SearchResult(GenericModel, Generic[RESOURCE_READ]):
    total_hits: int = Field(description="The total number of results.")
    resources: list[RESOURCE_READ] = Field(description="The resources matching the search query.")
    limit: int = Field(
        description="The maximum number of returned results, as specified in the " "input."
    )
    offset: int = Field(description="The offset, as specified in the input.")


class SearchRouter(Generic[RESOURCE], abc.ABC):
    """
    Providing search functionality in ElasticSearch
    """

    @property
    @abc.abstractmethod
    def es_index(self) -> str:
        """The name of the elasticsearch index"""

    @property
    @abc.abstractmethod
    def resource_name_plural(self) -> str:
        """The name of the resource (plural)"""

    @property
    def key_translations(self) -> dict[str, str]:
        """If an attribute is called differently in elasticsearch than in our
        metadata model, you can define a translation dictionary here. The key
        should be the name in elasticsearch, the value the name in our data
        model."""
        return {}

    @property
    @abc.abstractmethod
    def resource_class(self) -> RESOURCE:
        """The resource class"""

    @property
    def global_indexed_fields(self) -> set[str]:
        """The set of indexed fields that are mandatory for every entity"""
        return {"name", "description_plain", "description_html"}

    @property
    def extra_indexed_fields(self) -> set[str]:
        """The set of other indexed fields in addition to the global ones"""
        return set()

    @property
    def indexed_fields(self) -> set[str]:
        """The set of indexed fields"""
        return set.union(self.global_indexed_fields, self.extra_indexed_fields)

    @property
    def linked_fields(self) -> set[str]:
        """The set of linked fields (those with aiod 'link' relations)"""
        return set()

    def create(self, url_prefix: str) -> APIRouter:
        router = APIRouter()
        read_class = resource_read(self.resource_class)  # type: ignore
        indexed_fields: TypeAlias = Literal[tuple(self.indexed_fields)]  # type: ignore

        @router.get(
            f"{url_prefix}/search/{self.resource_name_plural}/v1",
            tags=["search"],
            description=f"""Search for {self.resource_name_plural}.""",
            # response_model=SearchResult[read_class],  # This gives errors, so not used.
        )
        def search(
            search_query: Annotated[
                str,
                Query(
                    description="The text to find. It is used in an ElasticSearch match query.",
                    examples=["Name of the resource"],
                ),
            ],
            exact_match: Annotated[
                bool,
                Query(
                    description="If true, it searches for an exact match.",
                ),
            ] = False,
            search_fields: Annotated[
                list[indexed_fields] | None,
                Query(
                    description="Search in these fields. If empty, the query will be matched "
                    "against all fields. Do not use the '--' option in Swagger, it is a Swagger "
                    "artifact.",
                ),
            ] = None,
            platforms: Annotated[
                list[str] | None,
                Query(
                    description="Search for resources of these platforms. If empty, results from "
                    "all platforms will be returned.",
                    examples=["huggingface", "openml"],
                ),
            ] = None,
            date_modified_after: Annotated[
                str | None,
                Query(
                    description="Search for resources modified after this date "
                    "(yyyy-mm-dd, inclusive).",
                    pattern="[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]",
                    examples=["2023-01-01"],
                ),
            ] = None,
            date_modified_before: Annotated[
                str | None,
                Query(
                    description="Search for resources modified before this date "
                    "(yyyy-mm-dd, not inclusive).",
                    pattern="[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]",
                    examples=["2023-01-01"],
                ),
            ] = None,
            sort_by_id: Annotated[
                bool,
                Query(
                    description="If true, the results are sorted by id."
                    "By default they are sorted by best score.",
                ),
            ] = False,
            limit: Annotated[int, Query(ge=1, le=LIMIT_MAX)] = 10,
            offset: Annotated[int, Query(ge=0)] = 0,
            get_all: Annotated[
                bool,
                Query(
                    description="If true, a request to the database is made to retrieve all data. "
                    "If false, only the indexed information is returned.",
                ),
            ] = False,
        ):
            try:
                with DbSession() as session:
                    query = select(Platform)
                    database_platforms = session.scalars(query).all()
                    platform_names = {p.name for p in database_platforms}
            except Exception as e:
                raise as_http_exception(e)

            if platforms and not set(platforms).issubset(platform_names):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"The available platforms are: {platform_names}",
                )

            fields = search_fields if search_fields else self.indexed_fields
            query_matches: list[dict[str, dict[str, str | dict[str, str]]]] = []
            if exact_match:
                query_matches = [
                    {"match": {f: {"query": search_query, "operator": "and"}}} for f in fields
                ]
            else:
                query_matches = [{"match": {f: search_query}} for f in fields]
            query = {"bool": {"should": query_matches, "minimum_should_match": 1}}
            must_clause = []
            if platforms:
                platform_matches = [{"match": {"platform": p}} for p in platforms]
                must_clause.append(
                    {"bool": {"should": platform_matches, "minimum_should_match": 1}}
                )
            if date_modified_after or date_modified_before:
                date_range = {}
                if date_modified_after:
                    date_range["gte"] = date_modified_after
                if date_modified_before:
                    date_range["lt"] = date_modified_before
                must_clause.append({"range": {"date_modified": date_range}})
            if must_clause:
                query["bool"]["must"] = must_clause
            sort: dict[str, str | dict[str, str]] = {}
            if sort_by_id:
                sort = {"identifier": "asc"}
            else:
                sort = {"_score": {"order": "desc"}}

            result = ElasticsearchSingleton().client.search(
                index=self.es_index, query=query, from_=offset, size=limit, sort=sort
            )
            total_hits = result["hits"]["total"]["value"]
            if get_all:
                identifiers = [hit["_source"]["identifier"] for hit in result["hits"]["hits"]]
                resources: list[SQLModel] = self._db_query(
                    read_class, self.resource_class, identifiers
                )
            else:
                resources: list[Type[read_class]] = [  # type: ignore
                    self._cast_resource(read_class, hit["_source"])
                    for hit in result["hits"]["hits"]
                ]
            return SearchResult[read_class](  # type: ignore
                total_hits=total_hits,
                resources=resources,
                limit=limit,
                offset=offset,
            )

        return router

    def _db_query(
        self,
        read_class: Type[SQLModel],
        resource_class: RESOURCE,
        identifiers: list[int],
    ) -> list[SQLModel]:
        try:
            with DbSession() as session:
                filter_ = resource_class.identifier.in_(identifiers)  # type: ignore[attr-defined]
                query = select(resource_class).where(filter_)
                resources = session.scalars(query).all()
                identifiers_found = {resource.identifier for resource in resources}
                identifiers_missing = set(identifiers) - identifiers_found
                if identifiers_missing:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Some resources, with identifiers "
                        f"{', '.join(map(str, identifiers_missing))}, could not be found in "
                        "the database.",
                    )
                return [read_class.from_orm(resource) for resource in resources]
        except Exception as e:
            raise as_http_exception(e)

    def _cast_resource(
        self, read_class: Type[SQLModel], resource_dict: dict[str, Any]
    ) -> Type[RESOURCE]:
        kwargs = {
            self.key_translations.get(key, key): val
            for key, val in resource_dict.items()
            if key != "type" and not key.startswith("@") and key not in self.linked_fields
        }
        resource = read_class(**kwargs)
        resource.aiod_entry = AIoDEntryRead(
            date_modified=resource_dict["date_modified"], status=None
        )
        resource.description = {
            "plain": resource_dict["description_plain"],
            "html": resource_dict["description_html"],
        }
        for linked_field in self.linked_fields:
            if resource_dict[linked_field]:
                setattr(resource, linked_field, resource_dict[linked_field].split(","))
        return resource
