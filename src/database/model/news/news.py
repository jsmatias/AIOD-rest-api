from sqlmodel import Field, Relationship

from database.model.ai_resource.resource import AbstractAIResource, AIResourceBase
from database.model.field_length import NORMAL
from database.model.helper_functions import many_to_many_link_factory
from database.model.news.news_category import NewsCategory
from database.model.relationships import ManyToMany
from database.model.serializers import AttributeSerializer, FindByNameDeserializer


class NewsBase(AIResourceBase):
    headline: str | None = Field(
        description="A short headline given to this news item.",
        max_length=NORMAL,
        schema_extra={"example": "A headline to show on top of the page."},
    )
    alternative_headline: str | None = Field(
        description="An alternative headline given to this news item.",
        max_length=NORMAL,
        schema_extra={"example": "An alternative headline."},
    )


class News(NewsBase, AbstractAIResource, table=True):  # type: ignore [call-arg]
    __tablename__ = "news"

    category: list[NewsCategory] = Relationship(
        link_model=many_to_many_link_factory("news", NewsCategory.__tablename__)
    )

    class RelationshipConfig(AbstractAIResource.RelationshipConfig):
        category: list[str] = ManyToMany(
            description="News categories related to this item.",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(NewsCategory),
            example=["research: education", "research: awards", "business: robotics"],
            default_factory_pydantic=list,
        )
