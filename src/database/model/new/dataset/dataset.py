from sqlmodel import Field

from database.model.new.concept import AIoDConceptBase, AIoDConcept
from database.model.new.resource import AIResourceBase, AIResource


class DatasetBase(AIResourceBase, AIoDConceptBase):
    version: str | None = Field(max_length=150, default=None, schema_extra={"example": "1.1.0"})


class DatasetNew(DatasetBase, AIResource, AIoDConcept, table=True):  # type: ignore [call-arg]
    __tablename__ = "dataset_new"

    class RelationshipConfig(AIResource.RelationshipConfig):
        pass
