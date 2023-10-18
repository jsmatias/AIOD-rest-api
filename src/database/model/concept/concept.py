import copy
import datetime
from typing import Optional, Tuple

from sqlalchemy import CheckConstraint, Column, Index
from sqlalchemy.util import classproperty
from sqlmodel import SQLModel, Field, Relationship

from database.model.concept.aiod_entry import AIoDEntryORM, AIoDEntryRead, AIoDEntryCreate
from database.model.field_length import SHORT, NORMAL
from database.model.helper_functions import get_relationships
from database.model.platform.platform_names import PlatformName
from database.model.relationships import OneToOne, DeleteOneToOne
from database.model.serializers import CastDeserializer


class AIoDConceptBase(SQLModel):
    """The AIoDConcept is the top-level (abstract) class in AIoD."""

    platform: str | None = Field(
        max_length=SHORT,
        default=None,
        description="The external platform from which this resource originates. Leave empty if "
        "this item originates from AIoD. If platform is not None, the "
        "platform_identifier should be set as well.",
        schema_extra={"example": PlatformName.example},
        foreign_key="platform.name",
    )
    platform_identifier: str | None = Field(
        max_length=NORMAL,
        description="A unique identifier issued by the external platform that's specified in "
        "'platform'. Leave empty if this item is not part of an external platform.",
        default=None,
        schema_extra={"example": "1"},
    )
    date_deleted: datetime.datetime | None = Field(exclude=True)


class AIoDConcept(AIoDConceptBase):
    identifier: int = Field(default=None, primary_key=True)
    aiod_entry_identifier: int | None = Field(
        foreign_key=AIoDEntryORM.__tablename__ + ".identifier"
    )
    aiod_entry: AIoDEntryORM = Relationship()

    def __init_subclass__(cls, metaclass=None):
        """Fixing problems with the inheritance of relationships."""
        cls.__annotations__.update(AIoDConcept.__annotations__)
        relationships = copy.deepcopy(AIoDConcept.__sqlmodel_relationships__)
        cls.__sqlmodel_relationships__.update(relationships)
        if cls.__tablename__ not in ("aiasset", "agent", "knowledgeasset", "airesource"):
            cls.create_triggers_based_on_configuration()

    class RelationshipConfig:
        aiod_entry: Optional[AIoDEntryRead] = OneToOne(
            deserializer=CastDeserializer(AIoDEntryORM),
            default_factory_orm=AIoDEntryORM,
            class_read=Optional[AIoDEntryRead],
            class_create=Optional[AIoDEntryCreate],
            on_delete_trigger_deletion_of=DeleteOneToOne(AIoDEntryORM, "aiod_entry_identifier"),
        )

    @classproperty
    def __table_args__(cls) -> Tuple:
        # Note to developer: this will give problems if we'll add another child which has extra
        # constraints, because this might lead to a duplicate check constraint name.
        # TODO: solve it when this becomes a problem.
        return (
            Index(
                f"{cls.__name__}_same_platform_and_platform_identifier",
                cls.platform,
                cls.platform_identifier,
                unique=True,
                postgresql_where=Column("date_deleted IS NULL"),
            ),
            CheckConstraint(
                "(platform IS NULL) <> (platform_identifier IS NOT NULL)",
                name=f"{cls.__name__}_platform_xnor_platform_id_null",
            ),
        )

    @classmethod
    def create_triggers_based_on_configuration(cls):
        for name, value in get_relationships(cls).items():
            value.create_triggers(cls)
