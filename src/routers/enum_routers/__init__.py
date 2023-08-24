from database.model.named_relation import NamedRelation
from routers.enum_routers.enum_router import EnumRouter
from routers.parent_router import non_abstract_subclasses

router_list: list[EnumRouter] = [
    EnumRouter(named_relation) for named_relation in non_abstract_subclasses(NamedRelation)
]
