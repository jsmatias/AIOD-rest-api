from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import SQLModel, Field


class EventApplicationAreaLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "event_application_area_link"
    event_identifier: int = Field(
        sa_column=Column(
            Integer, ForeignKey("event.identifier", ondelete="CASCADE"), primary_key=True
        )
    )
    application_area_identifier: int = Field(
        foreign_key="application_area_old.identifier", primary_key=True
    )
