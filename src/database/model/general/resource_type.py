from typing import List
from typing import TYPE_CHECKING

from sqlmodel import Relationship

if TYPE_CHECKING:  # avoid circular imports; only import while type checking
    from database.model.publication.publication import PublicationOld
from database.model.named_relation import NamedRelation


class ResourceType(NamedRelation, table=True):  # type: ignore [call-arg]
    """
    Keywords or tags used to describe some item
    """

    __tablename__ = "resource_type"

    publications: List["PublicationOld"] = Relationship(back_populates="resource_type")
