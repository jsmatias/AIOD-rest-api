from typing import List
from typing import TYPE_CHECKING

from sqlmodel import Relationship
from database.model.computational_resource.application_area_link import (
    ComputationalResourceApplicationAreaLink,
)

from database.model.event.application_area_link import EventApplicationAreaLink


if TYPE_CHECKING:  # avoid circular imports; only import while type checking
    from database.model.event.event import Event
    from database.model.computational_resource.computational_resource import ComputationalResource
from database.model.named_relation import NamedRelation


class ApplicationArea(NamedRelation, table=True):  # type: ignore [call-arg]
    """
    Application area used to describe some item
    """

    __tablename__ = "application_area_old"

    events: List["Event"] = Relationship(
        back_populates="application_areas", link_model=EventApplicationAreaLink
    )
    computational_resources: List["ComputationalResource"] = Relationship(
        back_populates="applicationArea", link_model=ComputationalResourceApplicationAreaLink
    )
