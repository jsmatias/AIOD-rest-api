from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import SQLModel, Field


class EducationalResourceLanguageLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "educational_resource_language_link"
    educational_resource_identifier: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("educational_resource.identifier", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    language_identifier: int = Field(foreign_key="language_old.identifier", primary_key=True)
