import copy

from sqlmodel import Field, Relationship

from database.model import AIAssetTable
from database.model.new.ai_asset.ai_asset import AIAssetBase, AIAsset
from database.model.new.helper_functions import link_factory
from database.model.new.knowledge_asset.knowledge_asset_table import KnowledgeAssetTable
from database.model.relationships import ResourceRelationshipList
from serialization import AttributeSerializer, FindByIdentifierDeserializer


class KnowledgeAssetBase(AIAssetBase):
    pass


class KnowledgeAsset(KnowledgeAssetBase, AIAsset):
    knowledge_asset_id: int | None = Field(
        foreign_key=KnowledgeAssetTable.__tablename__ + ".identifier"
    )
    knowledge_asset_identifier: KnowledgeAssetTable | None = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"}
    )

    documents: list[AIAssetTable] = Relationship(sa_relationship_kwargs={"cascade": "all, delete"})

    def __init_subclass__(cls):
        # TODO(Jos): describe what's going on here
        cls.__annotations__.update(KnowledgeAsset.__annotations__)
        relationships = copy.deepcopy(KnowledgeAsset.__sqlmodel_relationships__)
        cls.update_relationships_asset(relationships)

        relationships["documents"].link_model = link_factory(
            table_from=cls.__tablename__, table_to="ai_asset", table_prefix="documents"
        )
        cls.__sqlmodel_relationships__.update(relationships)

    class RelationshipConfig(AIAsset.RelationshipConfig):
        documents: list[int] = ResourceRelationshipList(
            description="The identifier of an AI asset for which the Knowledge Asset acts as an "
            "information source",
            serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializer(AIAssetTable),
            example=[],
            default_factory_pydantic=list,
        )
