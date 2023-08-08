from sqlmodel import SQLModel, Field


class AIoDConceptBase(SQLModel):
    pass


class AIoDConcept(AIoDConceptBase):
    identifier: int = Field(default=None, primary_key=True)
