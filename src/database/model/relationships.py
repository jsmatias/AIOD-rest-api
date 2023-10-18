"""
Together with the serializers and the resource_read_and_create, this adds additional
functionality on top of SQLModel so that a model only needs to be defined once, but supports
serialization and complex relationships.
"""

import abc
import dataclasses
from typing import Any, Type

from pydantic.utils import Representation
from sqlmodel import Field, SQLModel

from database.deletion.triggers import (
    create_deletion_trigger_one_to_x,
    create_deletion_trigger_many_to_many,
)
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
    def create_triggers(self, parent_class: Type[SQLModel]):
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
class DeleteOneToOne:
    """
    Delete rows from other table when a row from the parent table is deleted.

    Args:
        to_delete_model (Type[SQLModel]): Delete rows from this table
        linking_identifier (str): Delete those rows where identifier equals the
        linking_identifier of the deleted item.
    """

    to_delete_model: Type[SQLModel]
    linking_identifier: str


@dataclasses.dataclass
class OneToOne(_ResourceRelationshipSingle):
    on_delete_trigger_deletion_of: None | DeleteOneToOne = None

    def create_triggers(self, parent_class: Type[SQLModel]):
        if self.on_delete_trigger_deletion_of:
            create_deletion_trigger_one_to_x(
                trigger=parent_class,
                trigger_identifier_link=self.on_delete_trigger_deletion_of.linking_identifier,
                to_delete=self.on_delete_trigger_deletion_of.to_delete_model,
            )


@dataclasses.dataclass
class DeleteManyToOne:
    """
    Delete rows from other table when a row from the parent table is deleted.

    Args:
        to_delete_model (Type[SQLModel]): Delete rows from this table
        to_delete_identifier (str): Delete those rows for which the to_delete_identifier equals
        the just deleted
    """

    to_delete_model: Type[SQLModel]
    to_delete_identifier: str


@dataclasses.dataclass
class ManyToOne(_ResourceRelationshipSingle):
    # on_delete_trigger_deletion_of_orphan: None | DeleteOther = None

    def create_triggers(self, parent_class: Type[SQLModel]):
        pass
        # if self.on_delete_trigger_deletion_of_orphan:
        #     create_deletion_trigger_many_to_one(
        #         trigger=parent_class,
        #         to_delete=self.on_delete_trigger_deletion_of_orphan.to_delete_model,
        #         to_delete_identifier=self.on_delete_trigger_deletion_of_orphan.to_delete_identifier
        #     )


@dataclasses.dataclass
class OneToMany(_ResourceRelationshipList):
    on_delete_trigger_deletion_of: None | Type[SQLModel] = None

    def create_triggers(self, parent_class: Type[SQLModel]):
        if self.on_delete_trigger_deletion_of:
            create_deletion_trigger_one_to_x(
                trigger=parent_class,
                trigger_identifier_link=self.identifier_name,
                to_delete=self.on_delete_trigger_deletion_of,
            )


@dataclasses.dataclass
class DeleteOrphan:
    link_model: Type[SQLModel]
    to_delete_model: Type[SQLModel]


@dataclasses.dataclass
class ManyToMany(_ResourceRelationshipList):
    on_delete_trigger_orphan_deletion: None | DeleteOrphan = None

    def create_triggers(self, parent_class: Type[SQLModel]):
        if self.on_delete_trigger_orphan_deletion:
            create_deletion_trigger_many_to_many(
                trigger=parent_class,
                link=self.on_delete_trigger_orphan_deletion.link_model,
                to_delete=self.on_delete_trigger_orphan_deletion.to_delete_model,
            )
