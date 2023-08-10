from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import SQLModel, Field


class ComputationalResourceKeywordLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "computational_resource_keyword_link"
    computational_resource_identifier: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("computational_resource.identifier", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    keyword_identifier: int = Field(foreign_key="keyword_old.identifier", primary_key=True)
