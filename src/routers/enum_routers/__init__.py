from database.model.named_relation import NamedRelation
from routers.enum_routers.enum_router import EnumRouter
from routers.parent_router import non_abstract_subclasses

__named_relations = sorted(non_abstract_subclasses(NamedRelation), key=lambda n: n.__tablename__)

router_list: list[EnumRouter] = [EnumRouter(n) for n in __named_relations]
