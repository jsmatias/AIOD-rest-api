from typing import Type

from database.model.agent.agent import Agent
from database.model.agent.agent_table import AgentTable
from routers.parent_class_router import ParentClassRouter


class AgentRouter(ParentClassRouter):
    @property
    def resource_name(self) -> str:
        return "agent"

    @property
    def resource_name_plural(self) -> str:
        return "agents"

    @property
    def parent_class(self) -> Type[Agent]:
        return Agent

    @property
    def parent_class_table(self) -> Type[AgentTable]:
        return AgentTable
