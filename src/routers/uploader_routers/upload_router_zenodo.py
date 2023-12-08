from typing import Annotated

from fastapi import APIRouter
from fastapi import File, Query, UploadFile, Path

from uploaders.zenodo_uploader import ZenodoUploader
from routers.uploader_router import UploaderRouter


class UploadRouterZenodo(UploaderRouter):
    def create(self, url_prefix: str) -> APIRouter:
        router = super().create(url_prefix)

        zenodo_uploader = ZenodoUploader()

        @router.post(url_prefix + "/upload/datasets/{identifier}/zenodo", tags=["upload"])
        def zenodo_upload(
            identifier: int = Path(
                description="The AIoD dataset identifier",
            ),
            file: UploadFile = File(
                title="File", description="This file will be uploaded to Zenodo"
            ),
            publish: Annotated[
                bool,
                Query(
                    title="Publish dataset",
                    description="When published, the dataset and files will be publicaly ccessible "
                    "and you will no longer be able to upload more files!",
                ),
            ] = False,
            token: str = Query(title="Zenodo Token", description="The access token of Zenodo"),
        ) -> int:
            return zenodo_uploader.handle_upload(identifier, publish, token, file)

        return router
