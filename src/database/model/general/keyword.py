from typing import List
from typing import TYPE_CHECKING

from sqlmodel import Relationship

from database.model.case_study.keyword_link import CaseStudyKeywordLink
from database.model.computational_resource.keyword_link import (
    ComputationalResourceKeywordLink,
)
from database.model.dataset.keyword_link import DatasetKeywordLink
from database.model.educational_resource.keyword_link import EducationalResourceKeywordLink
from database.model.named_relation import NamedRelation
from database.model.news.keyword_link import NewsKeywordLink
from database.model.project.keyword_link import ProjectKeywordLink

if TYPE_CHECKING:  # avoid circular imports; only import while type checking
    from database.model.computational_resource.computational_resource import ComputationalResource
    from database.model.dataset.dataset import Dataset
    from database.model.news.news import News
    from database.model.educational_resource.educational_resource import EducationalResource
    from database.model.case_study.case_study import CaseStudy
    from database.model.project.project import Project


class KeywordOld(NamedRelation, table=True):  # type: ignore [call-arg]
    """
    Keywords or tags used to describe some item
    """

    __tablename__ = "keyword_old"

    case_studies: List["CaseStudy"] = Relationship(
        back_populates="keywords", link_model=CaseStudyKeywordLink
    )
    computational_resources: List["ComputationalResource"] = Relationship(
        back_populates="keyword", link_model=ComputationalResourceKeywordLink
    )
    datasets: List["Dataset"] = Relationship(
        back_populates="keywords", link_model=DatasetKeywordLink
    )
    educational_resources: List["EducationalResource"] = Relationship(
        back_populates="keywords", link_model=EducationalResourceKeywordLink
    )
    projects: List["Project"] = Relationship(
        back_populates="keywords", link_model=ProjectKeywordLink
    )
    news: List["News"] = Relationship(back_populates="keywords", link_model=NewsKeywordLink)
