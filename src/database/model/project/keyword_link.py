from sqlalchemy import Integer, ForeignKey, Column
from sqlmodel import SQLModel, Field


class ProjectKeywordLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "project_keyword_link"
    project_identifier: int = Field(
        sa_column=Column(
            Integer, ForeignKey("project.identifier", ondelete="CASCADE"), primary_key=True
        )
    )
    keyword_identifier: int = Field(foreign_key="keyword_old.identifier", primary_key=True)
