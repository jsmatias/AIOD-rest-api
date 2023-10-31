"""
The AIResource table, which is linked to every child of the AbstractAIResource (e.g. Dataset).
"""

from sqlmodel import SQLModel, Field, Relationship

from database.model.relationships import ResourceRelationshipList
from database.model.serializers import (
    create_getter_dict,
    AttributeSerializer,
    FindByIdentifierDeserializer,
)


class AIResourcePartLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "ai_resource_part_link"
    parent_identifier: int = Field(foreign_key="ai_resource.identifier", primary_key=True)
    child_identifier: int = Field(foreign_key="ai_resource.identifier", primary_key=True)


class AIResourceRelevantLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "ai_resource_relevant_link"
    parent_identifier: int = Field(foreign_key="ai_resource.identifier", primary_key=True)
    relevant_identifier: int = Field(foreign_key="ai_resource.identifier", primary_key=True)


class AIResourceBase(SQLModel):
    pass


class AIResourceORM(AIResourceBase, table=True):  # type: ignore [call-arg]
    __tablename__ = "ai_resource"
    identifier: int = Field(default=None, primary_key=True)
    type: str = Field(default="will be overwritten by resource_router")

    is_part_of: list["AIResourceORM"] = Relationship(
        back_populates="has_part",
        link_model=AIResourcePartLink,
        sa_relationship_kwargs={
            "primaryjoin": "AIResourceORM.identifier==AIResourcePartLink.parent_identifier",
            "secondaryjoin": "AIResourceORM.identifier==AIResourcePartLink.child_identifier",
        },
    )
    has_part: list["AIResourceORM"] = Relationship(
        back_populates="is_part_of",
        link_model=AIResourcePartLink,
        sa_relationship_kwargs={
            "primaryjoin": "AIResourceORM.identifier==AIResourcePartLink.child_identifier",
            "secondaryjoin": "AIResourceORM.identifier==AIResourcePartLink.parent_identifier",
        },
    )
    relevant_resource: list["AIResourceORM"] = Relationship(
        back_populates="relevant_to",
        link_model=AIResourceRelevantLink,
        sa_relationship_kwargs={
            "primaryjoin": "AIResourceORM.identifier==AIResourceRelevantLink.relevant_identifier",
            "secondaryjoin": "AIResourceORM.identifier==AIResourceRelevantLink.parent_identifier",
        },
    )
    relevant_to: list["AIResourceORM"] = Relationship(
        back_populates="relevant_resource",
        link_model=AIResourceRelevantLink,
        sa_relationship_kwargs={
            "primaryjoin": "AIResourceORM.identifier==AIResourceRelevantLink.parent_identifier",
            "secondaryjoin": "AIResourceORM.identifier==AIResourceRelevantLink.relevant_identifier",
        },
    )

    class RelationshipConfig:
        is_part_of: list[int] = ResourceRelationshipList()
        has_part: list[int] = ResourceRelationshipList()
        relevant_resource: list[int] = ResourceRelationshipList()
        relevant_to: list[int] = ResourceRelationshipList()


deserializer = FindByIdentifierDeserializer(AIResourceORM)
AIResourceORM.RelationshipConfig.is_part_of.deserializer = deserializer  # type: ignore
AIResourceORM.RelationshipConfig.has_part.deserializer = deserializer  # type: ignore
AIResourceORM.RelationshipConfig.relevant_resource.deserializer = deserializer  # type: ignore
AIResourceORM.RelationshipConfig.relevant_to.deserializer = deserializer  # type: ignore


class AIResourceCreate(AIResourceBase):
    is_part_of: list[int] = Field(
        description="A list of resource identifiers that this resource is a part of.",
        default_factory=list,
        schema_extra={"example": []},
    )
    has_part: list[int] = Field(
        description="A list of resource identifiers that are part of this resource.",
        default_factory=list,
        schema_extra={"example": []},
    )
    relevant_resource: list[int] = Field(
        description="A list of resource identifiers that are relevant to this resource.",
        default_factory=list,
        schema_extra={"example": []},
    )
    relevant_to: list[int] = Field(
        description="A list of resource identifiers to which this resource is relevant.",
        default_factory=list,
        schema_extra={"example": []},
    )


class AIResourceRead(AIResourceBase):
    identifier: int = Field(default=None, primary_key=True)
    type: str = Field(
        description="The name of the resource.",
    )
    is_part_of: list[int] = Field(
        description="A list of resource identifiers that this resource is a part of.",
        default_factory=list,
        schema_extra={"example": []},
    )
    has_part: list[int] = Field(
        description="A list of resource identifiers that are part of this resource.",
        default_factory=list,
        schema_extra={"example": []},
    )
    relevant_resource: list[int] = Field(
        description="A list of resource identifiers that are relevant to this resource.",
        default_factory=list,
        schema_extra={"example": []},
    )
    relevant_to: list[int] = Field(
        description="A list of resource identifiers to which this resource is relevant.",
        default_factory=list,
        schema_extra={"example": []},
    )

    class Config:
        getter_dict = create_getter_dict(
            {
                "is_part_of": AttributeSerializer("identifier"),
                "has_part": AttributeSerializer("identifier"),
                "relevant_resource": AttributeSerializer("identifier"),
                "relevant_to": AttributeSerializer("identifier"),
            }
        )
