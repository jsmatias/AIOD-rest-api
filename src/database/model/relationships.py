"""
Together with the serializers and the resource_read_and_create, this adds additional
functionality on top of SQLModel so that a model only needs to be defined once, but supports
serialization and complex relationships.
"""

import abc
import dataclasses
import typing
from types import UnionType
from typing import Any, Type, Callable

from pydantic.utils import Representation
from sqlmodel import Field, SQLModel

from database.deletion import triggers
from database.model import serializers


@dataclasses.dataclass
class _ResourceRelationship(abc.ABC, Representation):
    serializer: serializers.Serializer | None = None
    deserializer: serializers.DeSerializer | None = None
    description: str | None = None
    include_in_create: bool = True
    default_factory_orm: Any | None = None
    default_factory_pydantic: Any | None = None
    class_read: Any | None = None  # only needed if class_read differs from class_create
    class_create: Any | None = None  # only needed if class_read differs from class_create

    def field(self):
        return Field(
            description=self.description,
            schema_extra={"example": self.example} if self.example is not None else None,
            default_factory=self.default_factory_pydantic,
        )

    @property
    @abc.abstractmethod
    def example(self):
        pass

    @abc.abstractmethod
    def create_triggers(self, parent_class: Type[SQLModel], field_name: str):
        pass


@dataclasses.dataclass
class _ResourceRelationshipSingle(_ResourceRelationship):
    """For one-to-one and many-to-one relationships"""

    identifier_name: str | None = None
    example: str | int | None = None


@dataclasses.dataclass
class _ResourceRelationshipList(_ResourceRelationship):
    """For many-to-many and one-to-many relationships."""

    example: list[Any] | None = None


@dataclasses.dataclass
class OneToOne(_ResourceRelationshipSingle):
    on_delete_trigger_deletion_by: None | str = None

    def create_triggers(self, parent_class: Type[SQLModel], field_name: str):
        if self.on_delete_trigger_deletion_by is not None:
            to_delete = parent_class.__annotations__[field_name]
            is_optional = typing.get_origin(to_delete) in (typing.Union, UnionType) and type(
                None
            ) in typing.get_args(to_delete)
            if is_optional:
                (to_delete,) = [
                    type_ for type_ in to_delete.__args__ if not isinstance(None, type_)
                ]
            triggers.create_deletion_trigger_one_to_x(
                trigger=parent_class,
                trigger_identifier_link=self.on_delete_trigger_deletion_by,
                to_delete=to_delete,
            )


@dataclasses.dataclass
class ManyToOne(_ResourceRelationshipSingle):
    on_delete_trigger_deletion_of_orphan: None | Type[SQLModel] = None

    def create_triggers(self, parent_class: Type[SQLModel], field_name: str):
        if self.on_delete_trigger_deletion_of_orphan is not None:
            to_delete_identifier = getattr(
                parent_class.RelationshipConfig, field_name
            ).identifier_name
            triggers.create_deletion_trigger_many_to_one(
                trigger=parent_class,
                to_delete=self.on_delete_trigger_deletion_of_orphan,
                trigger_identifier_link=to_delete_identifier,
            )


@dataclasses.dataclass
class OneToMany(_ResourceRelationshipList):
    on_delete_trigger_deletion: None | str = None

    def create_triggers(self, parent_class: Type[SQLModel], field_name: str):
        if self.on_delete_trigger_deletion is not None:
            to_delete = parent_class.__annotations__[field_name].__args__[0]
            triggers.create_deletion_trigger_one_to_x(
                trigger=parent_class,
                to_delete=to_delete,
                to_delete_identifier=self.on_delete_trigger_deletion,
            )


@dataclasses.dataclass
class ManyToMany(_ResourceRelationshipList):
    on_delete_trigger_orphan_deletion: bool | Callable[[], list[str]] = False

    def create_triggers(self, parent_class: Type[SQLModel], field_name: str):
        if self.on_delete_trigger_orphan_deletion:
            link = parent_class.__sqlmodel_relationships__[field_name].link_model
            to_delete = parent_class.__annotations__[field_name].__args__[0]
            other_links = None
            if not isinstance(self.on_delete_trigger_orphan_deletion, bool):
                other_links = self.on_delete_trigger_orphan_deletion()
            triggers.create_deletion_trigger_many_to_many(
                trigger=parent_class, link=link, to_delete=to_delete, other_links=other_links
            )
