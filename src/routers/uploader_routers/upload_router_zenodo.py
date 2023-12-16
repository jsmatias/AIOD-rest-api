from typing import Annotated

from fastapi import APIRouter
from fastapi import File, Query, UploadFile, Path

from uploaders.zenodo_uploader import ZenodoUploader
from routers.uploader_router import UploaderRouter


class UploadRouterZenodo(UploaderRouter):
    def create(self, url_prefix: str) -> APIRouter:
        router = APIRouter()

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
                    description="Publish the dataset to Zenodo. When published, "
                    "the dataset and files will be publicly accessible "
                    "and you will no longer be able to upload more files!",
                ),
            ] = False,
            token: str = Query(title="Zenodo Token", description="The access token of Zenodo"),
        ) -> int:
            """
            Uploads a dataset to Zenodo using the AIoD metadata identifier.
            If the metadata does not exist on Zenodo
            (i.e., the platform_resource_identifier is None),
            a new repository will be created on Zenodo.
            """
            return zenodo_uploader.handle_upload(identifier, publish, token, file)

        return router
