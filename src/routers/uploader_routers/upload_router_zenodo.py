from fastapi import APIRouter
from fastapi import File, Query, UploadFile
from sqlalchemy.engine import Engine

from uploader.zenodo_uploader import handle_upload_


class UploadRouterZenodo:
    def create(self, engine: Engine, url_prefix: str) -> APIRouter:
        router = APIRouter()

        @router.post(url_prefix + "/upload/datasets/{identifier}/zenodo", tags=["upload"])
        def zenodo_upload(
            identifier: int,
            file: UploadFile = File(
                ..., title="File", description="This file will be uploaded to Zenodo"
            ),
            token: str = Query(..., title="Zenodo Token", description="The access token of Zenodo"),
        ) -> int:
            return handle_upload_(engine, identifier, file, token)

        return router
