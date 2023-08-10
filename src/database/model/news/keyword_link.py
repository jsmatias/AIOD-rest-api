from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import SQLModel, Field


class NewsKeywordLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "news_keyword_link"
    news_identifier: int = Field(
        sa_column=Column(
            Integer, ForeignKey("news.identifier", ondelete="CASCADE"), primary_key=True
        )
    )
    keyword_identifier: int = Field(foreign_key="keyword_old.identifier", primary_key=True)
