from typing import Optional

from sqlmodel import Field, Relationship

from database.model.agent.language import Language
from database.model.agent.location import Location, LocationORM
from database.model.ai_resource.resource import AbstractAIResource, AIResourceBase
from database.model.educational_resource.access_mode import AccessMode
from database.model.educational_resource.educational_level import EducationalLevel
from database.model.educational_resource.educational_resource_type import EducationalResourceType
from database.model.educational_resource.pace import Pace
from database.model.educational_resource.prerequisite import Prerequisite
from database.model.educational_resource.target_audience import TargetAudience
from database.model.field_length import NORMAL
from database.model.helper_functions import many_to_many_link_factory
from database.model.relationships import ManyToOne, ManyToMany
from database.model.serializers import AttributeSerializer, FindByNameDeserializer, CastDeserializer


class EducationalResourceBase(AIResourceBase):
    time_required: str | None = Field(
        description="An approximate or recommendation of the time required to use or complete the "
        "educational resource.",
        max_length=NORMAL,
        schema_extra={"example": "2 months"},
    )


class EducationalResource(
    EducationalResourceBase, AbstractAIResource, table=True
):  # type: ignore [call-arg]
    __tablename__ = "educational_resource"

    type_identifier: int | None = Field(
        foreign_key=EducationalResourceType.__tablename__ + ".identifier"
    )
    type: Optional[EducationalResourceType] = Relationship()
    pace_identifier: int | None = Field(foreign_key=Pace.__tablename__ + ".identifier")
    pace: Optional[Pace] = Relationship()
    access_mode: list[AccessMode] = Relationship(
        link_model=many_to_many_link_factory(
            table_from="educational_resource", table_to=AccessMode.__tablename__
        )
    )
    educational_level: list[EducationalLevel] = Relationship(
        link_model=many_to_many_link_factory(
            table_from="educational_resource", table_to=EducationalLevel.__tablename__
        )
    )
    in_language: list[Language] = Relationship(
        link_model=many_to_many_link_factory(
            table_from="educational_resource", table_to=Language.__tablename__
        )
    )
    location: list[LocationORM] = Relationship(
        link_model=many_to_many_link_factory("educational_resource", LocationORM.__tablename__)
    )
    prerequisite: list[Prerequisite] = Relationship(
        link_model=many_to_many_link_factory("educational_resource", Prerequisite.__tablename__)
    )
    target_audience: list[TargetAudience] = Relationship(
        link_model=many_to_many_link_factory(
            table_from="educational_resource", table_to=TargetAudience.__tablename__
        )
    )

    class RelationshipConfig(AbstractAIResource.RelationshipConfig):
        type: Optional[str] = ManyToOne(
            description="The type of educational resource.",
            identifier_name="type_identifier",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(EducationalResourceType),
            example="presentation",
        )
        pace: Optional[str] = ManyToOne(
            description="The high-level study schedule available for this educational resource. "
            '"self-paced" is mostly used for MOOCS, Tutorials and short courses '
            'without interactive elements; "scheduled" is used for scheduled courses '
            "with interactive elements that is not a full-time engagement; "
            '"full-time" is used for programmes or intensive courses that require a '
            "full-time engagement from the student.",
            identifier_name="pace_identifier",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(Pace),
            example="full-time",
        )
        access_mode: list[str] = ManyToMany(
            description="The primary mode of accessing this educational resource.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(AccessMode),
            example=["textual"],
            default_factory_pydantic=list,
        )
        educational_level: list[str] = ManyToMany(
            description="The level or levels of education for which this resource is intended.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(EducationalLevel),
            example=["primary school", "secondary school", "university"],
            default_factory_pydantic=list,
        )
        in_language: list[str] = ManyToMany(
            description="The language(s) of the educational resource, in ISO639-3.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(Language),
            example=["eng", "fra", "spa"],
            default_factory_pydantic=list,
        )
        location: list[Location] = ManyToMany(
            deserializer=CastDeserializer(LocationORM),
            default_factory_pydantic=list,
        )
        prerequisite: list[str] = ManyToMany(
            description="Minimum or recommended requirements to make use of this "
            "educational resource.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(Prerequisite),
            example=[
                "undergraduate knowledge of statistics",
                "graduate knowledge of linear algebra",
            ],
            default_factory_pydantic=list,
        )
        target_audience: list[str] = ManyToMany(
            description="The intended users of this educational resource.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(TargetAudience),
            example=[
                "professionals",
                "students in higher education",
                "teachers in secondary school",
            ],
            default_factory_pydantic=list,
        )
