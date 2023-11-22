# from .upload_router__huggingface import UploadRouterHuggingface
from .upload_router_zenodo import UploadRouterZenodo

router_list = [UploadRouterZenodo()]
