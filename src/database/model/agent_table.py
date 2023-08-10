from sqlmodel import SQLModel, Field


class AgentTable(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "agent_old"

    """
    Many resources, such as organisation and member, are a type of Agent
    and should therefore inherit from this Agent class.
    Shared fields can be defined on this class.

    Notice the difference between Agent and AgentTable.
    The latter enables defining a relationship to "any Agent",
    by making sure that the identifiers of all resources that
    are Agents, are unique over the Agents.
    """
    identifier: int = Field(
        default=None,
        primary_key=True,
        description="The identifier of each agent should be the same as this identifier",
    )
    type: str = Field(
        description="The name of the table of the asset. E.g. 'organisation' or 'member'"
    )
