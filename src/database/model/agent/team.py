from typing import Optional

from pydantic import condecimal
from sqlmodel import Field, Relationship

from database.model.agent.organisation import Organisation
from database.model.agent.person import Person
from database.model.ai_resource.resource import AIResourceBase
from database.model.ai_resource.resource import AbstractAIResource
from database.model.helper_functions import many_to_many_link_factory
from database.model.relationships import ManyToOne, ManyToMany
from database.model.serializers import AttributeSerializer, FindByIdentifierDeserializerList


class TeamBase(AIResourceBase):
    price_per_hour_euro: condecimal(max_digits=7, decimal_places=2) | None = Field(  # type: ignore
        description="A ballpark figure of the per hour cost to hire this team.",
        schema_extra={"example": 175.50},
        default=None,
    )
    size: int | None = Field(
        description="The number of persons that are part of this team.",
        schema_extra={"example": 10},
        default=None,
    )


class Team(TeamBase, AbstractAIResource, table=True):  # type: ignore [call-arg]
    __tablename__ = "team"

    organisation_identifier: int | None = Field(
        foreign_key=Organisation.__tablename__ + ".identifier"
    )
    organisation: Optional[Organisation] = Relationship()
    member: list[Person] = Relationship(
        link_model=many_to_many_link_factory("team", Person.__tablename__, "member"),
    )

    class RelationshipConfig(AbstractAIResource.RelationshipConfig):
        organisation: int | None = ManyToOne(
            description="The organisation of which this team is a part.",
            identifier_name="organisation_identifier",
            _serializer=AttributeSerializer("identifier"),
        )
        member: list[int] = ManyToMany(
            description="The persons that are a member of this team. The leader should "
            "also be added as contact.",
            _serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializerList(Person),
            example=[],
            default_factory_pydantic=list,
        )
