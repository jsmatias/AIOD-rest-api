from .computational_asset_router import ComputationalAssetRouter
from .dataset_router import DatasetRouter
from .experiment_router import ExperimentRouter
from .ml_model_router import MLModelRouter
from .organisation_router import OrganisationRouter
from .person_router import PersonRouter
from .platform_router import PlatformRouter
from .publication_router import PublicationRouter
from .resource_router import ResourceRouter  # noqa:F401
from .service_router import ServiceRouter
from .team_router import TeamRouter
from .upload_router_huggingface import UploadRouterHuggingface

resource_routers = [
    PlatformRouter(),
    # CaseStudyRouter(),
    ComputationalAssetRouter(),
    DatasetRouter(),
    # EducationalResourceRouter(),
    # EventRouter(),
    ExperimentRouter(),
    MLModelRouter(),
    # NewsRouter(),
    OrganisationRouter(),
    PersonRouter(),
    PublicationRouter(),
    # ProjectRouter(),
    # PresentationRouter(),
    ServiceRouter(),
    TeamRouter(),
]  # type: list[ResourceRouter]

other_routers = [UploadRouterHuggingface()]
