from . import resource_router_list
from .resource_router import ResourceRouter  # noqa:F401
from .parent_class_router import ParentClassRouter  # noqa:F401
from .parent_routers.agent_router import AgentRouter
from .upload_router_huggingface import UploadRouterHuggingface


resource_routers = resource_router_list.resource_routers

parent_class_routers = [AgentRouter()]  # type: list[ParentClassRouter]

other_routers = [UploadRouterHuggingface()]
