from fastapi import APIRouter
from fastapi import File, Query, UploadFile
from sqlalchemy.engine import Engine

from uploaders.zenodo_uploader import ZenodoUploader
from routers.uploader_router import UploaderRouter


class UploadRouterZenodo(UploaderRouter):
    def create(self, engine: Engine, url_prefix: str) -> APIRouter:
        router = super().create(engine, url_prefix)

        zenodo_uploader = ZenodoUploader()

        @router.post(url_prefix + "/upload/datasets/{identifier}/zenodo", tags=["upload"])
        def zenodo_upload(
            identifier: int,
            file: UploadFile = File(
                ..., title="File", description="This file will be uploaded to Zenodo"
            ),
            token: str = Query(..., title="Zenodo Token", description="The access token of Zenodo"),
        ) -> int:
            return zenodo_uploader.handle_upload(engine, identifier, token, file)

        return router
