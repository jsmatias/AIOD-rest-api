import abc
import copy
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship

from database.model import AIAssetTable
from database.model.new.ai_asset.distribution import Distribution, distribution_for_table
from database.model.new.ai_asset.license import License
from database.model.new.ai_resource.resource import AIResourceBase, AIResource
from database.model.new.field_length import NORMAL
from database.model.relationships import ResourceRelationshipSingle, ResourceRelationshipList
from serialization import AttributeSerializer, CastDeserializer, FindByNameDeserializer


class AIAssetBase(AIResourceBase, metaclass=abc.ABCMeta):
    date_published: datetime | None = Field(
        description="The datetime on which this AIAsset was first published on an external "
        "platform. ",
        default=None,
        schema_extra={"example": "2022-01-01T15:15:00.000Z"},
    )
    version: str | None = Field(max_length=NORMAL, default=None, schema_extra={"example": "1.1.0"})


class AIAsset(AIAssetBase, AIResource, metaclass=abc.ABCMeta):
    asset_id: int | None = Field(foreign_key=AIAssetTable.__tablename__ + ".identifier")
    asset_identifier: AIAssetTable | None = Relationship()

    # TODO: citation -- Publication
    distribution: list = Relationship(sa_relationship_kwargs={"cascade": "all, delete"})
    license_identifier: int | None = Field(foreign_key=License.__tablename__ + ".identifier")
    license: Optional[License] = Relationship()
    # TODO: creator -- Person

    def __init_subclass__(cls):
        # TODO(Jos): describe what's going on here
        cls.__annotations__.update(AIAsset.__annotations__)
        relationships = copy.deepcopy(AIAsset.__sqlmodel_relationships__)
        cls.update_relationships(relationships)
        distribution = distribution_for_table(table_from=cls.__tablename__)
        cls.__annotations__["distribution"] = list[distribution]
        cls.RelationshipConfig.distribution = copy.copy(cls.RelationshipConfig.distribution)
        cls.RelationshipConfig.distribution.deserializer = CastDeserializer(distribution)
        cls.__sqlmodel_relationships__.update(relationships)

    class RelationshipConfig(AIResource.RelationshipConfig):
        asset_identifier: int | None = ResourceRelationshipSingle(
            identifier_name="asset_id",
            serializer=AttributeSerializer("identifier"),
            include_in_create=False,
            default_factory_orm=lambda type_: AIAssetTable(type=type_),
        )
        distribution: list[Distribution] = ResourceRelationshipList(default_factory_pydantic=list)
        license: Optional[str] = ResourceRelationshipSingle(
            identifier_name="license_identifier",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(License),
            example="https://creativecommons.org/share-your-work/public-domain/cc0/",
        )
