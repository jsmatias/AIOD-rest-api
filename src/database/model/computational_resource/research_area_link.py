from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import SQLModel, Field


class ComputationalResourceResearchAreaLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "computational_resource_research_area_link"
    computational_resource_identifier: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("computational_resource.identifier", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    research_area_identifier: int = Field(
        foreign_key="research_area_old.identifier", primary_key=True
    )
