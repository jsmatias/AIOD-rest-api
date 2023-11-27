from routers.uploader_router import UploaderRouter
from .upload_router_zenodo import UploadRouterZenodo
from .upload_router_huggingface import UploadRouterHuggingface

router_list: list[UploaderRouter] = [UploadRouterZenodo(), UploadRouterHuggingface()]
