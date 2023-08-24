from .resource_router import ResourceRouter  # noqa:F401
from .resource_routers.case_study_router import CaseStudyRouter
from .resource_routers.computational_asset_router import ComputationalAssetRouter
from .resource_routers.dataset_router import DatasetRouter
from .resource_routers.educational_resource_router import EducationalResourceRouter
from .resource_routers.event_router import EventRouter
from .resource_routers.experiment_router import ExperimentRouter
from .resource_routers.ml_model_router import MLModelRouter
from .resource_routers.news_router import NewsRouter
from .resource_routers.organisation_router import OrganisationRouter
from .resource_routers.person_router import PersonRouter
from .resource_routers.platform_router import PlatformRouter
from .resource_routers.publication_router import PublicationRouter
from .resource_routers.service_router import ServiceRouter
from .resource_routers.team_router import TeamRouter

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
