from datetime import date
from typing import Optional

from sqlmodel import Field, Relationship

from database.model.new.agent.agent import AgentBase, Agent
from database.model.new.agent.agent_table import AgentTable
from database.model.new.agent.organisation_type import OrganisationType
from database.model.new.field_length import NORMAL, DESCRIPTION
from database.model.new.helper_functions import link_factory
from database.model.relationships import ResourceRelationshipSingle, ResourceRelationshipList
from serialization import AttributeSerializer, FindByNameDeserializer, FindByIdentifierDeserializer


class OrganisationBase(AgentBase):
    date_founded: date | None = Field(
        description="The date on which the organisation was founded.",
        schema_extra={"example": "2022-01-01"},
    )
    legal_name: str | None = Field(
        description="The official legal name of the organisation.",
        schema_extra={"example": "The Organisation Name"},
        max_length=NORMAL,
    )
    ai_relevance: str | None = Field(
        description="A description of positioning of the organisation within "
        "the broader European AI ecosystem.",
        schema_extra={"example": "Part of CLAIRE, focussing on explainable AI."},
        max_length=DESCRIPTION,
    )


class Organisation(OrganisationBase, Agent, table=True):  # type: ignore [call-arg]
    __tablename__ = "organisation"

    organisation_type_identifier: int | None = Field(
        foreign_key=OrganisationType.__tablename__ + ".identifier"
    )
    organisation_type: Optional[OrganisationType] = Relationship()

    member: list[AgentTable] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"},
        link_model=link_factory("organisation", AgentTable.__tablename__),
    )

    class RelationshipConfig(Agent.RelationshipConfig):
        organisation_type: Optional[str] = ResourceRelationshipSingle(
            description="The type of organisation.",
            identifier_name="organisation_type_identifier",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(OrganisationType),
            example=["Research Institution"],
        )
        member: list[int] = ResourceRelationshipList(
            description="The identifier of an agent (e.g. organisation or person) that is a "
            "member of this organisation.",
            serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializer(AgentTable),
            default_factory_pydantic=list,
        )
