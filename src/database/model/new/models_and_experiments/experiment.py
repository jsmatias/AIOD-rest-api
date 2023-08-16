from sqlmodel import Field

from database.model.new.ai_asset.ai_asset import AIAssetBase, AIAsset
from database.model.new.field_length import SHORT


class ExperimentBase(AIAssetBase):
    pid: str | None = Field(
        description="A permanent identifier for the model, for example a digital object "
        "identifier (DOI). Ideally a url.",
        max_length=SHORT,
        default=None,
        schema_extra={"example": "https://doi.org/10.1000/182"},
    )


class Experiment(ExperimentBase, AIAsset, table=True):  # type: ignore [call-arg]
    __tablename__ = "experiment"

    class RelationshipConfig(AIAsset.RelationshipConfig):
        pass
