from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import SQLModel, Field


class OrganisationMemberLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "organisation_member_link"
    organisation_identifier: int = Field(
        sa_column=Column(
            Integer, ForeignKey("organisation.identifier", ondelete="CASCADE"), primary_key=True
        )
    )
    member_identifier: int = Field(
        sa_column=Column(
            Integer, ForeignKey("agent_old.identifier", ondelete="CASCADE"), primary_key=True
        )
    )
