from typing import Annotated

from fastapi import APIRouter, Path
from fastapi import File, Query, UploadFile

from uploader.hugging_face_uploader import handle_upload


class UploadRouterHuggingface:
    def create(self, url_prefix: str) -> APIRouter:
        router = APIRouter()

        @router.post(url_prefix + "/upload/datasets/{identifier}/huggingface", tags=["upload"])
        def huggingFaceUpload(
            identifier: Annotated[
                int,
                Path(
                    description="The AIoD dataset identifier",
                ),
            ],
            file: Annotated[
                UploadFile,
                File(title="File", description="This file will be uploaded to HuggingFace"),
            ],
            token: Annotated[
                str, Query(title="Huggingface Token", description="The access token of HuggingFace")
            ],
            username: Annotated[
                str, Query(title="Huggingface username", description="The username of HuggingFace")
            ],
        ) -> int:
            return handle_upload(identifier, file, token, username)

        return router
