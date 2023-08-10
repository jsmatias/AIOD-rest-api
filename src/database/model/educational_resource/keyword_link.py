from sqlalchemy import Column, Integer, ForeignKey
from sqlmodel import SQLModel, Field


class EducationalResourceKeywordLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "educational_resource_keyword_link"
    educational_resource_identifier: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("educational_resource.identifier", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    keyword_identifier: int = Field(foreign_key="keyword_old.identifier", primary_key=True)
