from sqlalchemy import Column, Integer, ForeignKey
from sqlmodel import SQLModel, Field


class CaseStudyKeywordLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "case_study_keyword_link"
    casestudy_identifier: int = Field(
        sa_column=Column(
            Integer, ForeignKey("case_study.identifier", ondelete="CASCADE"), primary_key=True
        )
    )
    keyword_identifier: int = Field(foreign_key="keyword_old.identifier", primary_key=True)
