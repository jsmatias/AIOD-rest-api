from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from database.model.new.concept.status import Status
from database.model.new.field_length import SHORT, NORMAL
from database.model.platform.platform_names import PlatformName
from database.model.relationships import ResourceRelationshipSingle, ResourceRelationshipList
from serialization import AttributeSerializer, FindByNameDeserializer, create_getter_dict


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.model.new.agent.person import Person


class AIoDEntryBase(SQLModel):
    """Metadata of the metadata: when was the metadata last updated, with what identifiers is it
    known on other platforms, etc."""

    platform: str | None = Field(
        max_length=SHORT,
        default=None,
        description="The external platform from which this resource originates. Leave empty if "
        "this item originates from AIoD. If platform is not None, the "
        "platform_identifier should be set as well.",
        schema_extra={"example": PlatformName.zenodo},
        foreign_key="platform.name",
    )
    platform_identifier: str | None = Field(
        max_length=NORMAL,
        description="A unique identifier issued by the external platform that's specified in "
        "'platform'. Leave empty if this item is not part of an external platform.",
        default=None,
        schema_extra={"example": "1"},
    )
    date_modified: datetime | None = Field(
        description="The datetime on which the metadata was last updated in the AIoD platform,"
        "in UTC.",
        schema_extra={"example": "2023-01-01T15:15:00.000"},
        default_factory=datetime.utcnow,  # Updated in the resource_router
    )  # TODO(jos): it would be nice to hide the dates in the CREATE classes
    date_created: datetime | None = Field(
        description="The datetime on which the metadata was first published on the AIoD platform, "
        "in UTC.",
        default_factory=datetime.utcnow,
        schema_extra={"example": "2022-01-01T15:15:00.000"},
    )


class AIoDEntryORM(AIoDEntryBase, table=True):  # type: ignore [call-arg]
    """Metadata of the metadata: when was the metadata last updated, with what identifiers is it
    known on other platforms, etc."""

    __tablename__ = "aiod_entry"

    identifier: int = Field(default=None, primary_key=True)
    editor: list["Person"] = Relationship()
    status_identifier: int | None = Field(foreign_key=Status.__tablename__ + ".identifier")
    status: Status = Relationship()

    class RelationshipConfig:
        editor: list[int] = ResourceRelationshipList()
        status: str = ResourceRelationshipSingle(
            example="draft",
            identifier_name="status_identifier",
            deserializer=FindByNameDeserializer(Status),
        )


class AIoDEntry(AIoDEntryBase):
    editor: list[int] = Field(
        description="Links to identifiers of persons responsible for maintaining the entry.",
        default_factory=list,
    )
    status: str = Field(
        description="Status of the entry (published, draft, rejected)",
        schema_extra={"example": "draft"},
    )

    class Config:
        getter_dict = create_getter_dict(
            {"editor": AttributeSerializer("identifier"), "status": AttributeSerializer("name")}
        )
