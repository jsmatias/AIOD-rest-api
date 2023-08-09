import typing  # noqa:F401

from .dataset_router_new import DatasetRouterNew
from .platform_router import PlatformRouter
from .publication_router import PublicationRouter
from .resource_router import ResourceRouter  # noqa:F401
from .upload_router_huggingface import UploadRouterHuggingface

resource_routers = [
    PlatformRouter(),
    DatasetRouterNew(),
    # CaseStudyRouter(),
    # ComputationalResourceRouter(),
    # DatasetRouter(),
    # EducationalResourceRouter(),
    # EventRouter(),
    # NewsRouter(),
    # OrganisationRouter(),
    PublicationRouter(),
    # ProjectRouter(),
    # PresentationRouter(),
]  # type: typing.List[ResourceRouter]

other_routers = [UploadRouterHuggingface()]
