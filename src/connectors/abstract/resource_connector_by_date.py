import abc
from datetime import datetime
from typing import Generic, TypeVar, Iterator
from connectors.record_error import RecordError

from sqlmodel import SQLModel

from connectors.resource_with_relations import ResourceWithRelations
from database.model.platform.platform_names import PlatformName


RESOURCE = TypeVar("RESOURCE", bound=SQLModel)


class ResourceConnectorByDate(abc.ABC, Generic[RESOURCE]):
    """
    For every platform that offers this resource, this ResourceConnector should be implemented.
    """

    @property
    @abc.abstractmethod
    def resource_class(self) -> type[RESOURCE]:
        pass

    @property
    @abc.abstractmethod
    def platform_name(self) -> PlatformName:
        """The platform of this connector"""
        pass

    @abc.abstractmethod
    def retry(self, id: str) -> SQLModel | ResourceWithRelations[SQLModel]:
        """Retrieve information of the resource identified by id"""
        pass

    @abc.abstractmethod
    def fetch(
        self, from_incl: datetime | None = None, to_excl: datetime | None = None
    ) -> Iterator[SQLModel | ResourceWithRelations[SQLModel] | RecordError]:
        """Retrieve information of all resources"""
        pass
