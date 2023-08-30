import abc
from typing import Union

from fastapi import APIRouter, HTTPException
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, select, Session
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from routers import resource_routers


class ParentRouter(abc.ABC):
    """
    Abstract class for FastAPI parent-class routers. These are routers for, for example, Agent,
    making it possible to perform a GET request based on the agent_identifier, retrieving either
    an Organisation or a Person.
    """

    @property
    @abc.abstractmethod
    def resource_name(self) -> str:
        """The name of the resource. E.g. 'agent'"""

    @property
    @abc.abstractmethod
    def resource_name_plural(self) -> str:
        """The plural of the name of the resource. E.g. 'agents'"""

    @property
    @abc.abstractmethod
    def parent_class(self):
        """The resource type. E.g. Agent"""

    @property
    @abc.abstractmethod
    def parent_class_table(self):
        """The table class of the resource. E.g. AgentTable"""

    def create(self, engine: Engine, url_prefix: str) -> APIRouter:
        router = APIRouter()
        version = "v1"
        default_kwargs = {
            "response_model_exclude_none": True,
            "tags": ["parents"],
        }
        available_schemas: list[SQLModel] = list(non_abstract_subclasses(self.parent_class))
        classes_dict = {clz.__tablename__: clz for clz in available_schemas if clz.__tablename__}
        routers = {router.resource_name: router for router in resource_routers.router_list}
        read_classes_dict = {name: routers[name].resource_class_read for name in classes_dict}
        response_model = Union[*read_classes_dict.values()]  # type:ignore

        router.add_api_route(
            path=url_prefix + f"/{self.resource_name_plural}/{version}/{{identifier}}",
            endpoint=self.get_resource_func(engine, classes_dict, read_classes_dict),
            response_model=response_model,  # type: ignore
            name=self.resource_name,
            **default_kwargs,
        )
        return router

    def get_resource_func(self, engine: Engine, classes_dict: dict, read_classes_dict: dict):
        def get_resource(identifier: int):
            with Session(engine) as session:
                query = select(self.parent_class_table).where(
                    self.parent_class_table.identifier == identifier
                )
                parent_resource = session.scalars(query).first()
                if not parent_resource:
                    raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail=f"{self.resource_name} with identifier {identifier} not found.",
                    )
                child_type: str = parent_resource.type
                child_class = classes_dict[child_type]
                child_class_read = read_classes_dict[child_type]
                query_child = select(child_class).where(
                    getattr(child_class, self.resource_name + "_id") == identifier
                )
                child = session.scalars(query_child).first()
                if not child:
                    raise HTTPException(
                        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"The parent could be found, but the child ({child_type}) was not "
                        f"found in our database",
                    )
                return child_class_read.from_orm(child)

        return get_resource


def non_abstract_subclasses(cls):
    """
    All non-abstract subclasses of the class.

    To check if a class is abstract, we check if it has any children itself. This will break if
    we ever inherit from a non-abstract class.
    """
    for child in cls.__subclasses__():
        has_grandchild = False
        for grand_child in non_abstract_subclasses(child):
            has_grandchild = True
            yield grand_child
        if not has_grandchild:
            yield child
