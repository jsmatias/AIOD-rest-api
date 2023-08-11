from typing import List
from typing import TYPE_CHECKING

from sqlmodel import Relationship
from database.model.educational_resource.language_link import EducationalResourceLanguageLink


if TYPE_CHECKING:  # avoid circular imports; only import while type checking
    from database.model.educational_resource.educational_resource import EducationalResource
from database.model.named_relation import NamedRelation


class LanguageOld(NamedRelation, table=True):  # type: ignore [call-arg]
    """
    Keywords or tags used to describe some item
    """

    __tablename__ = "language_old"

    educational_resources: List["EducationalResource"] = Relationship(
        back_populates="languages", link_model=EducationalResourceLanguageLink
    )
