from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, SQLModel


def ai_resource_keyword_link(table_name: str):
    class KeywordLink(SQLModel, table=True):  # type: ignore [call-arg]
        __tablename__ = table_name + "_keyword_link"
        resource_identifier: int = Field(
            sa_column=Column(
                Integer,
                ForeignKey(table_name + ".identifier", ondelete="CASCADE"),
                primary_key=True,
            )
        )
        keyword_identifier: int = Field(foreign_key="keyword.identifier", primary_key=True)

    return KeywordLink
