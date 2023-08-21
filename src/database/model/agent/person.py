from sqlmodel import Relationship, Field

from database.model.agent.agent import AgentBase, Agent
from database.model.agent.expertise import Expertise
from database.model.agent.language import Language
from database.model.ai_resource.resource import AIResource
from database.model.concept.aiod_entry import AIoDEntryORM
from database.model.field_length import NORMAL
from database.model.helper_functions import link_factory
from database.model.relationships import ResourceRelationshipList
from database.model.serializers import (
    AttributeSerializer,
    FindByNameDeserializer,
    FindByIdentifierDeserializer,
)


class PersonBase(AgentBase):
    given_name: str | None = Field(
        description="Also known as forename or first name. The part of the personal name that "
        "identifies a person, potentially with a middle name as well.",
        max_length=NORMAL,
        schema_extra={"example": "Jane"},
    )
    surname: str | None = Field(
        description="Also known as last name or family name. The mostly heriditary part of the "
        "personal name.",
        max_length=NORMAL,
        schema_extra={"example": "Doe"},
    )


class Person(PersonBase, Agent, table=True):  # type: ignore [call-arg]
    __tablename__ = "person"

    expertise: list[Expertise] = Relationship(
        link_model=link_factory("person", Expertise.__tablename__)
    )
    language: list[Language] = Relationship(
        link_model=link_factory("person", Language.__tablename__)
    )
    # TODO(jos): memberOf? This should probably be on Agent

    class RelationshipConfig(Agent.RelationshipConfig):
        expertise: list[str] = ResourceRelationshipList(
            description="A skill this person masters.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(Expertise),
            example=["transfer learning"],
            default_factory_pydantic=list,
        )
        language: list[str] = ResourceRelationshipList(
            description="A language this person masters, in ISO639-3",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(Language),
            example=["eng", "fra", "spa"],
            default_factory_pydantic=list,
        )


deserializer = FindByIdentifierDeserializer(Person)
AIResource.RelationshipConfig.contact.deserializer = deserializer  # type: ignore
AIoDEntryORM.RelationshipConfig.editor.deserializer = deserializer  # type: ignore
