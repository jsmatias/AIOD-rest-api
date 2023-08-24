from .case_study_router import CaseStudyRouter
from .dataset_router import DatasetRouter
from .educational_resource_router import EducationalResourceRouter
from .event_router import EventRouter
from .experiment_router import ExperimentRouter
from .ml_model_router import MLModelRouter
from .news_router import NewsRouter
from .organisation_router import OrganisationRouter
from .person_router import PersonRouter
from .platform_router import PlatformRouter
from .publication_router import PublicationRouter
from .resource_router import ResourceRouter  # noqa:F401
from .service_router import ServiceRouter
from .team_router import TeamRouter
from .computational_asset_router import ComputationalAssetRouter

resource_routers = [
    PlatformRouter(),
    CaseStudyRouter(),
    ComputationalAssetRouter(),
    DatasetRouter(),
    EducationalResourceRouter(),
    EventRouter(),
    ExperimentRouter(),
    MLModelRouter(),
    NewsRouter(),
    OrganisationRouter(),
    PersonRouter(),
    PublicationRouter(),
    # ProjectRouter(),
    ServiceRouter(),
    TeamRouter(),
]  # type: list[ResourceRouter]
