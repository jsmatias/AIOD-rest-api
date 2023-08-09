from sqlmodel import Field

from database.model.new.ai_asset.asset import AIAssetBase, AIAsset


class PublicationBase(AIAssetBase):
    measurement_technique: str | None = Field(
        max_length=150, schema_extra={"example": "TODO"}, default=None
    )


class PublicationNew(PublicationBase, AIAsset, table=True):  # type: ignore [call-arg]
    __tablename__ = "publication_new"

    class RelationshipConfig(AIAsset.RelationshipConfig):
        pass
