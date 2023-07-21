import abc
from typing import Generic, Iterator, TypeVar

from sqlmodel import SQLModel
from connectors.abstract.resource_connector import ResourceConnector

from connectors.resource_with_relations import ResourceWithRelations

from connectors.record_error import RecordError

RESOURCE = TypeVar("RESOURCE", bound=SQLModel)


class ResourceConnectorById(ResourceConnector, Generic[RESOURCE]):
    """
    For every platform that offers this resource, this ResourceConnector should be implemented.
    """

    @abc.abstractmethod
    def retry(self, id: int) -> SQLModel | ResourceWithRelations[SQLModel] | RecordError:
        """Retrieve information of the resource identified by id"""
        pass

    @abc.abstractmethod
    def fetch(
        self, from_id: int | None = None, to_id: int | None = None
    ) -> Iterator[SQLModel | ResourceWithRelations[SQLModel] | RecordError]:
        """Retrieve information of all resources"""
        pass
