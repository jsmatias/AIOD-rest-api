import abc
import copy
from typing import Any

from sqlmodel import Field, Relationship

from database.model.new.ai_asset.distribution import Distribution, distribution_for_table
from database.model.new.ai_resource.alternate_name import AlternateName
from database.model.new.ai_resource.application_area import ApplicationArea
from database.model.new.ai_resource.industrial_sector import IndustrialSector
from database.model.new.ai_resource.keyword import Keyword
from database.model.new.ai_resource.research_area import ResearchArea
from database.model.new.ai_resource.resource_table import AIResourceTable
from database.model.new.ai_resource.scientific_domain import ScientificDomain
from database.model.new.concept.concept import AIoDConceptBase, AIoDConcept
from database.model.new.field_length import SHORT, DESCRIPTION, NORMAL
from database.model.new.helper_functions import link_factory
from database.model.relationships import ResourceRelationshipSingle, ResourceRelationshipList
from serialization import (
    AttributeSerializer,
    FindByNameDeserializer,
    CastDeserializer,
    FindByIdentifierDeserializer,
)


class AIResourceBase(AIoDConceptBase, metaclass=abc.ABCMeta):
    name: str = Field(max_length=SHORT, schema_extra={"example": "The name of this resource"})
    description: str = Field(max_length=DESCRIPTION, schema_extra={"example": "A description."})
    same_as: str | None = Field(
        description="Url of a reference Web page that unambiguously indicates this resource's "
        "identity.",
        max_length=NORMAL,
        default=None,
        schema_extra={"example": "https://www.example.com/resource/this_resource"},
    )


class AIResource(AIResourceBase, AIoDConcept, metaclass=abc.ABCMeta):
    resource_id: int | None = Field(foreign_key="ai_resource.identifier")
    resource_identifier: AIResourceTable | None = Relationship()

    alternate_name: list[AlternateName] = Relationship()
    keyword: list[Keyword] = Relationship()

    application_area: list[ApplicationArea] = Relationship()
    industrial_sector: list[IndustrialSector] = Relationship()
    research_area: list[ResearchArea] = Relationship()
    scientific_domain: list[ScientificDomain] = Relationship()

    is_part_of: list[AIResourceTable] = Relationship()
    has_part: list[AIResourceTable] = Relationship()

    media: list = Relationship(sa_relationship_kwargs={"cascade": "all, delete"})

    def __init_subclass__(cls):
        # TODO(Jos): describe what's going on here
        cls.__annotations__.update(AIResource.__annotations__)
        relationships = copy.deepcopy(AIResource.__sqlmodel_relationships__)
        if cls.__tablename__ != "aiasset":
            cls.update_relationships(relationships)
        cls.__sqlmodel_relationships__.update(relationships)

    class RelationshipConfig(AIoDConcept.RelationshipConfig):
        resource_identifier: int | None = ResourceRelationshipSingle(
            description="This resource can be identified by its own identifier, but also by the "
            "resource_identifier.",
            identifier_name="resource_id",
            serializer=AttributeSerializer("identifier"),
            include_in_create=False,
            default_factory_orm=lambda type_: AIResourceTable(type=type_),
        )
        alternate_name: list[str] = ResourceRelationshipList(
            description="An alias for the item, commonly used for the resource instead of the "
            "name.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(AlternateName),
            example=["alias 1", "alias 2"],
            default_factory_pydantic=list,
        )
        keyword: list[str] = ResourceRelationshipList(
            description="Keywords or tags used to describe this resource, providing additional "
            "context.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(Keyword),
            example=["keyword1", "keyword2"],
            default_factory_pydantic=list,
        )

        application_area: list[str] = ResourceRelationshipList(
            description="The objective of this AI resource.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(ApplicationArea),
            example=["Fraud Prevention", "Voice Assistance", "Disease Classification"],
            default_factory_pydantic=list,
        )
        industrial_sector: list[str] = ResourceRelationshipList(
            description="A business domain where a resource is or can be used.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(IndustrialSector),
            example=["Finance", "eCommerce", "Healthcare"],
            default_factory_pydantic=list,
        )
        research_area: list[str] = ResourceRelationshipList(
            description="The research area is similar to the scientific_domain, but more "
            "high-level.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(ResearchArea),
            example=["Explainable AI", "Physical AI"],
            default_factory_pydantic=list,
        )
        scientific_domain: list[str] = ResourceRelationshipList(
            description="The scientific domain is related to the methods with which an objective "
            "is reached.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(ScientificDomain),
            example=["Anomaly Detection", "Voice Recognition", "Computer Vision."],
            default_factory_pydantic=list,
        )
        # TODO(jos): documentedIn - KnowledgeAsset
        # TODO(jos): contact - Person
        # decided to remove Location here. What does it mean for e.g. a dataset to reside at an
        # address of at a geographical location?
        media: list[Distribution] = ResourceRelationshipList(
            description="Images or videos depicting the resource or associated with it. ",
            default_factory_pydantic=list,
        )

        is_part_of: list[int] = ResourceRelationshipList(
            description="Links to identifiers of parent resources, which include this resource.",
            serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializer(AIResourceTable),
            default_factory_pydantic=list,
            example=[],
        )
        has_part: list[int] = ResourceRelationshipList(
            description="Links to identifiers of child resources, which are included in this "
            "resource.",
            serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializer(AIResourceTable),
            default_factory_pydantic=list,
            example=[],
        )

    @classmethod
    def update_relationships(cls, relationships: dict[str, Any]):
        distribution: Any = distribution_for_table(
            table_from=cls.__tablename__, distribution_name="media"
        )
        cls.__annotations__["media"] = list[distribution]
        cls.RelationshipConfig.media = copy.copy(cls.RelationshipConfig.media)
        cls.RelationshipConfig.media.deserializer = CastDeserializer(distribution)  # type: ignore

        for table_to in (
            "alternate_name",
            "keyword",
            "application_area",
            "industrial_sector",
            "research_area",
            "scientific_domain",
        ):
            relationships[table_to].link_model = link_factory(
                table_from=cls.__tablename__, table_to=table_to
            )
        relationships["has_part"].link_model = link_factory(
            table_from=cls.__tablename__,
            table_to=AIResourceTable.__tablename__,
            table_prefix="has_part",
        )
        relationships["is_part_of"].link_model = link_factory(
            table_from=cls.__tablename__,
            table_to=AIResourceTable.__tablename__,
            table_prefix="is_part_of",
        )
