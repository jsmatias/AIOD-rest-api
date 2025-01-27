from typing import Optional

from sqlmodel import Field, Relationship

from database.model.ai_asset.ai_asset import AIAssetBase, AIAsset
from database.model.field_length import SHORT
from database.model.helper_functions import link_factory
from database.model.models_and_experiments.experiment import Experiment
from database.model.models_and_experiments.ml_model_type import MLModelType
from database.model.models_and_experiments.runnable_distribution import RunnableDistribution
from database.model.relationships import ResourceRelationshipList, ResourceRelationshipSingle
from database.model.serializers import (
    AttributeSerializer,
    FindByIdentifierDeserializer,
    FindByNameDeserializer,
)


class MLModelBase(AIAssetBase):
    pid: str | None = Field(
        description="A permanent identifier for the model, for example a digital object "
        "identifier (DOI). Ideally a url.",
        max_length=SHORT,
        default=None,
        schema_extra={"example": "https://doi.org/10.1000/182"},
    )


class MLModel(MLModelBase, AIAsset, table=True):  # type: ignore [call-arg]
    __tablename__ = "ml_model"

    related_experiment: list["Experiment"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"},
        link_model=link_factory("ml_model", Experiment.__tablename__),
    )
    type_identifier: int | None = Field(foreign_key=MLModelType.__tablename__ + ".identifier")
    type: Optional[MLModelType] = Relationship()

    class RelationshipConfig(AIAsset.RelationshipConfig):
        distribution: list[RunnableDistribution] = ResourceRelationshipList(
            default_factory_pydantic=list
        )
        type: str | None = ResourceRelationshipSingle(
            description="The type of machine learning model.",
            identifier_name="type_identifier",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(MLModelType),
            example="Large Language Model",
        )
        related_experiment: list[int] = ResourceRelationshipList(
            description="Related experiments.",
            serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializer(Experiment),
            default_factory_pydantic=list,
            example=[],
        )
