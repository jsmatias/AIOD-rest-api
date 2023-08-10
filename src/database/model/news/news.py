from datetime import datetime
from typing import List
from sqlmodel import Field, Relationship
from database.model.general.keyword import KeywordOld
from database.model.general.business_category import BusinessCategory
from database.model.general.media import Media
from database.model.general.news_category import NewsCategory
from database.model.news.keyword_link import NewsKeywordLink
from database.model.news.media_link import NewsMediaLink
from database.model.news.news_category_link import NewsCategoryNewsLink
from database.model.news.business_category_link import NewsBusinessCategoryLink
from database.model.relationships import ResourceRelationshipList
from serialization import (
    AttributeSerializer,
    FindByNameDeserializer,
)
from database.model.resource import Resource


class NewsBase(Resource):
    # Required fields
    title: str = Field(max_length=150, schema_extra={"example": "Example News"})
    date_modified: datetime | None = Field(
        default=None, schema_extra={"example": "2022-01-01T15:15:00.000Z"}
    )
    body: str = Field(max_length=2000, schema_extra={"example": "Example news body"})
    section: str = Field(max_length=500, schema_extra={"example": "Example news section"})
    headline: str = Field(max_length=500, schema_extra={"example": "Example news headline"})
    word_count: int = Field(schema_extra={"example": 100})
    # Recommended fields
    source: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "https://news.source.example"}
    )
    alternative_headline: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "Example news alternative headline"}
    )


class News(NewsBase, table=True):  # type: ignore [call-arg]
    __tablename__ = "news"
    identifier: int = Field(default=None, primary_key=True)
    news_categories: List[NewsCategory] = Relationship(
        back_populates="news", link_model=NewsCategoryNewsLink
    )
    media: List[Media] = Relationship(back_populates="news", link_model=NewsMediaLink)
    keywords: List[KeywordOld] = Relationship(back_populates="news", link_model=NewsKeywordLink)
    business_categories: List[BusinessCategory] = Relationship(
        back_populates="news", link_model=NewsBusinessCategoryLink
    )

    class RelationshipConfig:
        news_categories: List[str] = ResourceRelationshipList(
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(NewsCategory),
            example=["news_category1", "news_category2"],
        )
        media: List[str] = ResourceRelationshipList(
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(Media),
            example=["media1", "media2"],
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
