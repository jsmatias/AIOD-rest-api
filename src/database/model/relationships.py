import abc
import dataclasses
from typing import Any

from pydantic.utils import Representation
from sqlmodel import Field

from serialization import Serializer, DeSerializer


def ResourceRelationshipList(*args, **kwargs) -> Any:
    """
    Describing many-to-many and one-to-many relationships.

    Wrapper around the class ResourceRelationshipInfo` to keep mypy happy. Similarly used to
    the function Relationship of Pydantic.
    """
    return ResourceRelationshipListInfo(*args, **kwargs)


def ResourceRelationshipSingle(*args, **kwargs) -> Any:
    """
    Describing many-to-one relationships.

    Wrapper around the class ResourceRelationshipInfo` to keep mypy happy. Similarly used to
    the function Relationship of Pydantic.
    """
    return ResourceRelationshipSingleInfo(*args, **kwargs)


@dataclasses.dataclass
class ResourceRelationshipInfo(abc.ABC, Representation):
    """
    For many-to-one relationships
    """

    serializer: Serializer | None = None
    deserializer: DeSerializer | None = None
    description: str | None = None
    include_in_create: bool = True
    default_factory: Any | None = None

    def field(self):
        return Field(description=self.description, schema_extra={"example": self.example})

    @property
    @abc.abstractmethod
    def example(self):
        pass


@dataclasses.dataclass
class ResourceRelationshipListInfo(ResourceRelationshipInfo):
    """For many-to-many and one-to-many relationships."""

    example: list[str] | list[int] | None = None


@dataclasses.dataclass
class ResourceRelationshipSingleInfo(ResourceRelationshipInfo):
    """For many-to-one relationships"""

    identifier_name: str | None = None
    example: str | int | None = None
