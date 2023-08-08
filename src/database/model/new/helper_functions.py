from collections import ChainMap
from typing import TYPE_CHECKING
from typing import Type

from sqlmodel import SQLModel

if TYPE_CHECKING:
    from database.model.relationships import ResourceRelationshipInfo


def _get_relationships(resource_class: Type[SQLModel]) -> dict[str, "ResourceRelationshipInfo"]:
    if not hasattr(resource_class, "RelationshipConfig"):
        return {}
    config = resource_class.RelationshipConfig
    return {field: getattr(config, field) for field in dir(config) if not field.startswith("_")}


def _all_annotations(cls) -> ChainMap:
    """Returns a dictionary-like ChainMap that includes annotations for all
    attributes defined in cls or inherited from superclasses.

    From
    https://stackoverflow.com/questions/63903901/how-can-i-access-to-annotations-of-parent-class
    """
    return ChainMap(*(c.__annotations__ for c in cls.__mro__ if "__annotations__" in c.__dict__))
