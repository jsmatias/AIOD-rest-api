import abc
import copy

from sqlmodel import Field, Relationship

from database.model.general.keyword import Keyword
from database.model.new.concept import AIoDConceptBase, AIoDConcept
from database.model.new.resource_links import ai_resource_keyword_link
from database.model.new.resource_table import AIResourceTable
from database.model.relationships import ResourceRelationshipSingle, ResourceRelationshipList
from serialization import AttributeSerializer, FindByNameDeserializer


class AIResourceBase(AIoDConceptBase, metaclass=abc.ABCMeta):
    name: str = Field(max_length=150, schema_extra={"example": "Example Dataset"})


class AIResource(AIResourceBase, AIoDConcept, metaclass=abc.ABCMeta):
    resource_id: int | None = Field(foreign_key="ai_resource.identifier")
    resource_identifier: AIResourceTable | None = Relationship()
    keywords: list[Keyword] = Relationship()

    def __init_subclass__(cls):
        # TODO(Jos): describe what's going on here
        cls.__annotations__.update(AIResource.__annotations__)
        relationships = copy.deepcopy(AIResource.__sqlmodel_relationships__)
        relationships["keywords"].link_model = ai_resource_keyword_link(
            table_name=cls.__tablename__
        )
        cls.__sqlmodel_relationships__.update(relationships)

    class RelationshipConfig:
        resource_identifier: int | None = ResourceRelationshipSingle(
            identifier_name="resource_id",
            serializer=AttributeSerializer("identifier"),
            include_in_create=False,
            default_factory=lambda type_: AIResourceTable(type=type_),
        )
        keywords: list[str] = ResourceRelationshipList(
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(Keyword),
            example=["keyword1", "keyword2"],
        )
