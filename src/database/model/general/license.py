from typing import List

from sqlmodel import Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # avoid circular imports; only import while type checking
    from database.model.dataset.dataset import Dataset
    from database.model.publication.publication import Publication
from database.model.named_relation import NamedRelation


class LicenseOld(NamedRelation, table=True):  # type: ignore [call-arg]
    """
    A license document, indicated by URL.
    """

    __tablename__ = "license_old"

    datasets: List["Dataset"] = Relationship(back_populates="license")
    publications: List["Publication"] = Relationship(back_populates="license")
