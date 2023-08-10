from datetime import datetime
from typing import List
from pydantic import condecimal

from sqlmodel import Field, Relationship
from database.model.relationships import ResourceRelationshipList
from serialization import (
    AttributeSerializer,
    FindByNameDeserializer,
)

from database.model.general.keyword import KeywordOld
from database.model.project.keyword_link import ProjectKeywordLink

from database.model.resource import Resource

MONEY_TYPE = condecimal(max_digits=12, decimal_places=2)


class ProjectBase(Resource):

    # Required fields
    name: str = Field(max_length=250, schema_extra={"example": "Example Project"})

    # Recommended fields
    doi: str | None = Field(max_length=150, schema_extra={"example": "0000000/000000000000"})
    start_date: datetime | None = Field(
        default=None, schema_extra={"example": "2022-01-01T15:15:00.000Z"}
    )
    end_date: datetime | None = Field(
        default=None, schema_extra={"example": "2023-01-01T15:15:00.000Z"}
    )
    founded_under: str | None = Field(
        max_length=250, default=None, schema_extra={"example": "John Doe"}
    )
    total_cost_euro: MONEY_TYPE | None = Field(  # type: ignore
        default=None, schema_extra={"example": 100000000.54}
    )
    eu_contribution_euro: MONEY_TYPE | None = Field(  # type: ignore
        default=None, schema_extra={"example": 100000000.54}
    )

    coordinated_by: str | None = Field(
        max_length=250, default=None, schema_extra={"example": "John Doe"}
    )
    project_description_title: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "A project description title"}
    )
    project_description_text: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "Example project description"}
    )
    programmes_url: str | None = Field(
        max_length=250, schema_extra={"example": "aiod.eu/project/0/programme"}
    )
    topic_url: str | None = Field(
        max_length=250, schema_extra={"example": "aiod.eu/project/0/topic"}
    )
    call_for_proposal: str | None = Field(
        max_length=250, schema_extra={"example": "Example call for proposal"}
    )
    founding_scheme: str | None = Field(max_length=250, schema_extra={"example": "founding scheme"})
    image: str | None = Field(max_length=250, schema_extra={"example": "Example image"})
    url: str | None = Field(max_length=250, schema_extra={"example": "aiod.eu/project/0"})


class Project(ProjectBase, table=True):  # type: ignore [call-arg]
    __tablename__ = "project"

    identifier: int = Field(default=None, primary_key=True)
    keywords: List[KeywordOld] = Relationship(
        back_populates="projects", link_model=ProjectKeywordLink
    )

    class RelationshipConfig:
        keywords: List[str] = ResourceRelationshipList(
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(KeywordOld),
            example=["keyword1", "keyword2"],
        )
