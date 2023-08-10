from typing import List
from typing import TYPE_CHECKING

from sqlmodel import Relationship
from database.model.computational_resource.research_area_link import (
    ComputationalResourceResearchAreaLink,
)
from database.model.event.research_area_link import EventResearchAreaLink


if TYPE_CHECKING:  # avoid circular imports; only import while type checking
    from database.model.event.event import Event
    from database.model.computational_resource.computational_resource import ComputationalResource
from database.model.named_relation import NamedRelation


class ResearchArea(NamedRelation, table=True):  # type: ignore [call-arg]
    """
    Research area used to describe some item
    """

    __tablename__ = "research_area_old"

    events: List["Event"] = Relationship(
        back_populates="research_areas", link_model=EventResearchAreaLink
    )
    computational_resources: List["ComputationalResource"] = Relationship(
        back_populates="researchArea", link_model=ComputationalResourceResearchAreaLink
    )
