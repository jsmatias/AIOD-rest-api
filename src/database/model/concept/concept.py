import copy
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from database.model.concept.aiod_entry import AIoDEntry, AIoDEntryORM
from database.model.relationships import ResourceRelationshipSingle
from serialization import CastDeserializer


class AIoDConceptBase(SQLModel):
    pass


class AIoDConcept(AIoDConceptBase):
    identifier: int = Field(default=None, primary_key=True)
    aiod_entry_identifier: int | None = Field(
        foreign_key=AIoDEntryORM.__tablename__ + ".identifier"
    )
    aiod_entry: AIoDEntryORM = Relationship()

    def __init_subclass__(cls):
        # TODO(Jos): describe what's going on here
        cls.__annotations__.update(AIoDConcept.__annotations__)
        relationships = copy.deepcopy(AIoDConcept.__sqlmodel_relationships__)
        cls.__sqlmodel_relationships__.update(relationships)

    class RelationshipConfig:
        aiod_entry: Optional[AIoDEntry] = ResourceRelationshipSingle(
            deserializer=CastDeserializer(AIoDEntryORM), default_factory_orm=AIoDEntryORM
        )
