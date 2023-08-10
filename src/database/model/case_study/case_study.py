from datetime import datetime
from typing import List

from sqlmodel import Field, Relationship
from database.model.case_study.alternate_name import (
    CaseStudyAlternateName,
    CaseStudyAlternateNameLink,
)

from database.model.relationships import ResourceRelationshipList
from database.model.resource import Resource
from serialization import (
    AttributeSerializer,
    FindByNameDeserializer,
)

from database.model.general.keyword import KeywordOld
from database.model.case_study.keyword_link import CaseStudyKeywordLink

from database.model.general.business_category import BusinessCategory
from database.model.case_study.business_category_link import CaseStudyBusinessCategoryLink

from database.model.general.technical_category import TechnicalCategory
from database.model.case_study.technical_category_link import CaseStudyTechnicalCategoryLink


class CaseStudyBase(Resource):
    # Required fields
    description: str = Field(max_length=5000, schema_extra={"example": "A description."})
    name: str = Field(max_length=150, schema_extra={"example": "Example Case Study"})

    # Recommended fields
    creator: str | None = Field(max_length=150, default=None, schema_extra={"example": "John Doe"})
    publisher: str | None = Field(
        max_length=150, default=None, schema_extra={"example": "John Doe"}
    )
    date_modified: datetime | None = Field(
        default=None, schema_extra={"example": "2023-01-01T15:15:00.000Z"}
    )
    date_published: datetime | None = Field(
        default=None, schema_extra={"example": "2022-01-01T15:15:00.000Z"}
    )
    same_as: str | None = Field(
        max_length=150,
        unique=True,
        schema_extra={"example": "https://www.example.com/case_study/example"},
    )
    url: str | None = Field(max_length=150, schema_extra={"example": "aiod.eu/case_study/0"})
    is_accessible_for_free: bool = Field(default=True)


class CaseStudy(CaseStudyBase, table=True):  # type: ignore [call-arg]
    __tablename__ = "case_study"

    identifier: int = Field(default=None, primary_key=True)
    alternate_names: List[CaseStudyAlternateName] = Relationship(
        back_populates="case_studies", link_model=CaseStudyAlternateNameLink
    )
    keywords: List[KeywordOld] = Relationship(
        back_populates="case_studies", link_model=CaseStudyKeywordLink
    )
    business_categories: List[BusinessCategory] = Relationship(
        back_populates="case_studies", link_model=CaseStudyBusinessCategoryLink
    )
    technical_categories: List[TechnicalCategory] = Relationship(
        back_populates="case_studies", link_model=CaseStudyTechnicalCategoryLink
    )

    class RelationshipConfig:
        alternate_names: List[str] = ResourceRelationshipList(
            example=["alias 1", "alias 2"],
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(CaseStudyAlternateName),
        )
        keywords: List[str] = ResourceRelationshipList(
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(KeywordOld),
            example=["keyword1", "keyword2"],
        )
        business_categories: List[str] = ResourceRelationshipList(
            example=["business category 1", "business category 2"],
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(BusinessCategory),
        )
        technical_categories: List[str] = ResourceRelationshipList(
            example=["technical category 1", "technical category 2"],
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(TechnicalCategory),
        )
