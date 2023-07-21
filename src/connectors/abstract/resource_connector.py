import abc

from typing import Generic, TypeVar


from sqlmodel import SQLModel


from database.model.platform.platform_names import PlatformName


RESOURCE = TypeVar("RESOURCE", bound=SQLModel)


class ResourceConnector(abc.ABC, Generic[RESOURCE]):
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
