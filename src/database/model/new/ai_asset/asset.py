import abc
import copy

from sqlmodel import Field, Relationship

from database.model import AIAssetTable
from database.model.new.ai_asset.distribution import Distribution, distribution_for_table
from database.model.new.ai_resource.resource import AIResourceBase, AIResource
from database.model.new.ai_resource.resource_links import ai_resource_keyword_link
from database.model.relationships import ResourceRelationshipSingle, ResourceRelationshipList
from serialization import AttributeSerializer, CastDeserializer


class AIAssetBase(AIResourceBase, metaclass=abc.ABCMeta):
    version: str | None = Field(max_length=150, default=None, schema_extra={"example": "1.1.0"})


class AIAsset(AIAssetBase, AIResource, metaclass=abc.ABCMeta):
    asset_id: int | None = Field(foreign_key=AIAssetTable.__tablename__ + ".identifier")
    asset_identifier: AIAssetTable | None = Relationship()

    distribution: list = Relationship(sa_relationship_kwargs={"cascade": "all, delete"})

    def __init_subclass__(cls):
        # TODO(Jos): describe what's going on here
        cls.__annotations__.update(AIAsset.__annotations__)
        relationships = copy.deepcopy(AIAsset.__sqlmodel_relationships__)
        relationships["keyword"].link_model = ai_resource_keyword_link(table_name=cls.__tablename__)
        distribution = distribution_for_table(cls.__tablename__)
        cls.__annotations__["distribution"] = list[distribution]
        cls.RelationshipConfig.distribution = copy.copy(cls.RelationshipConfig.distribution)
        cls.RelationshipConfig.distribution.deserializer = CastDeserializer(distribution)
        cls.__sqlmodel_relationships__.update(relationships)

    class RelationshipConfig(AIResource.RelationshipConfig):
        asset_identifier: int | None = ResourceRelationshipSingle(
            identifier_name="asset_id",
            serializer=AttributeSerializer("identifier"),
            include_in_create=False,
            default_factory=lambda type_: AIAssetTable(type=type_),
        )
        distribution: list[Distribution] = ResourceRelationshipList()
