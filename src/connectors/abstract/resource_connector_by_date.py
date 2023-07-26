import abc
from datetime import datetime
from typing import Generic, Iterator, TypeVar
from connectors.abstract.resource_connector import ResourceConnector
from connectors.record_error import RecordError

from sqlmodel import SQLModel

from connectors.resource_with_relations import ResourceWithRelations

RESOURCE = TypeVar("RESOURCE", bound=SQLModel)


class ResourceConnectorByDate(ResourceConnector, Generic[RESOURCE]):
    """
    For every platform that offers this resource, this ResourceConnector should be implemented.
    """

    @abc.abstractmethod
    def retry(self, _id: int) -> SQLModel | ResourceWithRelations[SQLModel] | RecordError:
        """Retrieve information of the resource identified by id"""
        pass

    @abc.abstractmethod
    def fetch(
        self, from_incl: datetime, to_excl: datetime
    ) -> Iterator[SQLModel | ResourceWithRelations[SQLModel] | RecordError]:
        """Retrieve information of all resources"""
        pass
