import typing  # noqa:F401

from .case_study_router import CaseStudyRouter
from .resource_router import ResourceRouter  # noqa:F401
from .dataset_router import DatasetRouter
from .news_router import NewsRouter
from .publication_router import PublicationRouter
from .educational_resource_router import EducationalResourceRouter
from .event_router import EventRouter
from .organisation_router import OrganisationRouter
from .project_router import ProjectRouter

routers = [
    CaseStudyRouter(),
    DatasetRouter(),
    EducationalResourceRouter(),
    EventRouter(),
    NewsRouter(),
    OrganisationRouter(),
    PublicationRouter(),
    ProjectRouter(),
]  # type: typing.List[ResourceRouter]