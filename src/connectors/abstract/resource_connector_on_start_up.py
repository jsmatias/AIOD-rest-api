import abc
from typing import Generic, Iterator, TypeVar
from connectors.abstract.resource_connector import ResourceConnector
from connectors.record_error import RecordError

from sqlmodel import SQLModel

from connectors.resource_with_relations import ResourceWithRelations

RESOURCE = TypeVar("RESOURCE", bound=SQLModel)


class ResourceConnectorOnStartUp(ResourceConnector, Generic[RESOURCE]):
    """
    For every platform that offers this resource, this ResourceConnector should be implemented.
    """

    @abc.abstractmethod
    def fetch(
        self, limit: int | None = None
    ) -> Iterator[SQLModel | ResourceWithRelations[SQLModel] | RecordError]:
        """Retrieve information of all resources"""
        pass
