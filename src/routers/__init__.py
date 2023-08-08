import typing  # noqa:F401

from .dataset_router_new import DatasetRouterNew
from .resource_router import ResourceRouter  # noqa:F401
from .case_study_router import CaseStudyRouter
from .computational_resource_router import ComputationalResourceRouter
from .dataset_router import DatasetRouter
from .educational_resource_router import EducationalResourceRouter
from .event_router import EventRouter
from .news_router import NewsRouter
from .organisation_router import OrganisationRouter
from .platform_router import PlatformRouter
from .presentation_router import PresentationRouter
from .project_router import ProjectRouter
from .publication_router import PublicationRouter
from .upload_router_huggingface import UploadRouterHuggingface

resource_routers = [
    PlatformRouter(),
    DatasetRouterNew(),
    CaseStudyRouter(),
    ComputationalResourceRouter(),
    DatasetRouter(),
    EducationalResourceRouter(),
    EventRouter(),
    NewsRouter(),
    OrganisationRouter(),
    PublicationRouter(),
    ProjectRouter(),
    PresentationRouter(),
]  # type: typing.List[ResourceRouter]

other_routers = [UploadRouterHuggingface()]
