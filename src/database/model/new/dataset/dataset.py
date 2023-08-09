from sqlmodel import Field

from database.model.new.ai_asset.asset import AIAssetBase, AIAsset


class DatasetBase(AIAssetBase):
    measurement_technique: str | None = Field(
        max_length=150, schema_extra={"example": "TODO"}, default=None
    )


class DatasetNew(DatasetBase, AIAsset, table=True):  # type: ignore [call-arg]
    __tablename__ = "dataset_new"

    class RelationshipConfig(AIAsset.RelationshipConfig):
        pass
