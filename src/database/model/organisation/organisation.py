from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship

from database.model.agent import Agent
from database.model.agent_table import AgentTable
from database.model.general.business_category import BusinessCategory
from database.model.general.technical_category import TechnicalCategory
from database.model.organisation.business_category_link import OrganisationBusinessCategoryLink
from database.model.organisation.email import (
    OrganisationEmail,
    OrganisationEmailLink,
)
from database.model.organisation.member_link import OrganisationMemberLink
from database.model.organisation.technical_category_link import OrganisationTechnicalCategoryLink
from database.model.relationships import ResourceRelationshipList, ResourceRelationshipSingle
from serialization import AttributeSerializer, FindByNameDeserializer, FindByIdentifierDeserializer


class OrganisationBase(Agent):
    # Required fields
    type: str = Field(max_length=500, schema_extra={"example": "Research Institution"})

    # Recommended fields
    connection_to_ai: str | None = Field(
        max_length=500,
        default=None,
        schema_extra={"example": "Example positioning in European AI ecosystem."},
    )
    logo_url: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "aiod.eu/project/0/logo"}
    )
    same_as: str | None = Field(
        max_length=500,
        unique=True,
        default=None,
        schema_extra={"example": "https://www.example.com/organisation/example"},
    )
    founding_date: datetime | None = Field(
        default=None, schema_extra={"example": "2022-01-01T15:15:00.000Z"}
    )
    dissolution_date: datetime | None = Field(
        default=None, schema_extra={"example": "2023-01-01T15:15:00.000Z"}
    )
    legal_name: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "Example official name"}
    )
    alternate_name: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "Example alternate name"}
    )
    address: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "Example address"}
    )
    telephone: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "Example telephone number"}
    )

    # TODO subsidiary_organisation_id not currently added. This is because
    # the relationship with organisation is nor clear, and is similar to departments.


class Organisation(OrganisationBase, table=True):  # type: ignore
    __tablename__ = "organisation"

    identifier: int = Field(primary_key=True, foreign_key="agent_old.identifier")

    parent_organisation_id: int | None = Field(foreign_key="organisation.identifier", default=None)
    parent_organisation: Optional["Organisation"] = Relationship(
        back_populates="departments",
        sa_relationship_kwargs=dict(
            remote_side="Organisation.identifier",
            cascade="all, delete",
        ),
    )

    business_categories: List[BusinessCategory] = Relationship(
        back_populates="organisations", link_model=OrganisationBusinessCategoryLink
    )
    technical_categories: List[TechnicalCategory] = Relationship(
        back_populates="organisations", link_model=OrganisationTechnicalCategoryLink
    )
    emails: List[OrganisationEmail] = Relationship(
        back_populates="organisations", link_model=OrganisationEmailLink
    )
    members: List["AgentTable"] = Relationship(
        link_model=OrganisationMemberLink,
    )
    departments: List["Organisation"] = Relationship(
        back_populates="parent_organisation",
    )

    class RelationshipConfig:

        business_categories: List[str] = ResourceRelationshipList(
            example=["business category 1", "business category 2"],
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(BusinessCategory),
        )
        technical_categories: List[str] = ResourceRelationshipList(
            example=["technical category 1", "technical category 2"],
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(TechnicalCategory),
        )
        emails: List[str] = ResourceRelationshipList(
            example=["email@org.com", "ceo@org.com"],
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(OrganisationEmail),
        )
        members: List[int] = ResourceRelationshipList(
            example=[],
            serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializer(AgentTable),
        )
        departments: List[int] = ResourceRelationshipList(
            example=[],
            serializer=AttributeSerializer("identifier"),
        )
        parent_organisation: int | None = ResourceRelationshipSingle(
            identifier_name="parent_organisation_id",
            serializer=AttributeSerializer("identifier"),
            example=1,  # Empty would be better, but using "None" results in example=0
        )


deserializer = FindByIdentifierDeserializer(Organisation)  # type: ignore
Organisation.RelationshipConfig.departments.deserializer = deserializer  # type: ignore
