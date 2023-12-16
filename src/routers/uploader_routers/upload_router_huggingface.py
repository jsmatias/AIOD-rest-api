from fastapi import APIRouter
from fastapi import File, Query, UploadFile

from routers.uploader_router import UploaderRouter
from uploaders.hugging_face_uploader import HuggingfaceUploader


class UploadRouterHuggingface(UploaderRouter):
    def create(self, url_prefix: str) -> APIRouter:
        router = APIRouter()

        hugging_face_uploader = HuggingfaceUploader()

        @router.post(url_prefix + "/upload/datasets/{identifier}/huggingface", tags=["upload"])
        def huggingFaceUpload(
            identifier: int,
            file: UploadFile = File(
                ..., title="File", description="This file will be uploaded to HuggingFace"
            ),
            token: str = Query(
                ..., title="Huggingface Token", description="The access token of HuggingFace"
            ),
            username: str = Query(
                ..., title="Huggingface username", description="The username of HuggingFace"
            ),
        ) -> int:
            return hugging_face_uploader.handle_upload(identifier, file, token, username)

        return router
