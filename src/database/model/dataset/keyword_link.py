from sqlalchemy import Column, Integer, ForeignKey
from sqlmodel import SQLModel, Field


class DatasetKeywordLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "dataset_keyword_link"
    dataset_identifier: int = Field(
        sa_column=Column(
            Integer, ForeignKey("dataset.identifier", ondelete="CASCADE"), primary_key=True
        )
    )
    keyword_identifier: int = Field(foreign_key="keyword_old.identifier", primary_key=True)
