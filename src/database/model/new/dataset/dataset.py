from sqlmodel import Field

from database.model.new.ai_asset.ai_asset import AIAssetBase, AIAsset


class DatasetBase(AIAssetBase):
    measurement_technique: str | None = Field(
        max_length=150, schema_extra={"example": "TODO"}, default=None
    )


class Dataset(DatasetBase, AIAsset, table=True):  # type: ignore [call-arg]
    __tablename__ = "dataset"

    class RelationshipConfig(AIAsset.RelationshipConfig):
        pass
