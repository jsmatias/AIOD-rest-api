import io

import huggingface_hub
from fastapi import HTTPException, UploadFile, status
from requests import HTTPError


from database.model.dataset.dataset import Dataset
from database.model.platform.platform_names import PlatformName
from database.session import DbSession
from database.validators import huggingface_validators
from uploaders.uploader import Uploader
from .utils import huggingface_license_identifiers


class HuggingfaceUploader(Uploader):
    def __init__(self) -> None:
        def repo_id_validator(repo_id: str, username: str):
            return _throw_error_on_invalid_repo_id(username, repo_id)

        super().__init__(PlatformName.huggingface, repo_id_validator)

    def handle_upload(self, identifier: int, file: UploadFile, token: str, username: str):
        with DbSession() as session:
            dataset: Dataset = self._get_resource(session=session, identifier=identifier)

            self._validate_platform_name(dataset.platform, identifier, allow_empty_name=False)

            repo_id = dataset.platform_resource_identifier
            self._validate_repo_id(repo_id, username)

            url = self._create_or_get_repo_url(repo_id, token)
            metadata_file = self._generate_metadata_file(dataset)
            try:
                huggingface_hub.upload_file(
                    path_or_fileobj=metadata_file,
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    repo_type="dataset",
                    token=token,
                )
            except HTTPError:
                msg = "Error updating the metadata, "
                "huggingface api returned a http error: {e.strerror}"
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)

            except ValueError as e:
                msg = f"Error updating the metadata, bad format: {e}"
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)
            except Exception:
                msg = "Error updating the metadata, unexpected error"
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)

            try:
                huggingface_hub.upload_file(
                    path_or_fileobj=io.BufferedReader(file.file),
                    path_in_repo=f"/data/{file.filename}",
                    repo_id=repo_id,
                    repo_type="dataset",
                    token=token,
                )
            except HTTPError as e:
                msg = (
                    f"Error uploading the file, huggingface api returned a http error: {e.strerror}"
                )
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)

            except ValueError:
                msg = "Error uploading the file, bad format"
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)
            except Exception as e:
                msg = f"Error uploading the file, unexpected error: {e.with_traceback}"
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)

            distribution_dict = {"name": repo_id, "content_url": url}
            self._store_resource_updated(session, dataset, distribution_dict)

            return dataset.identifier

    def _create_or_get_repo_url(self, repo_id, token):
        try:
            url = huggingface_hub.create_repo(repo_id, repo_type="dataset", token=token)
            return url
        except Exception as e:
            if "You already created this dataset repo" in e.args[0]:
                return f"https://huggingface.co/datasets/{repo_id}"
            else:
                msg = f"Unexpected error while creating the repository: {e}"
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg) from e

    def _generate_metadata_file(self, dataset: Dataset) -> bytes:
        tags = ["- " + tag.name for tag in dataset.keyword] if dataset.keyword else []
        content = "---\n"
        content += f"pretty_name: {dataset.name}\n"

        if tags:
            content += "tags:\n"
            content += "\n".join(tags) + "\n"
        # TODO the license must be in the huggingface format:
        #  https://huggingface.co/docs/hub/repositories-licenses

        if dataset.license in huggingface_license_identifiers:
            content += f"license: {dataset.license.name if dataset.license else ''}"

        content += "---\n"
        content += f"# {dataset.name}\n"
        content += "Created from AIOD platform"  # TODO add url
        return content.encode("utf-8")


def _throw_error_on_invalid_repo_id(username: str, platform_resource_identifier: str):
    """
    Return a valid repository identifier, including namespace, for Huggingface, or raise an error,

    Valid repo_ids:
        Between 1 and 96 characters.
        Either “repo_name” or “namespace/repo_name”
        [a-zA-Z0-9] or ”-”, ”_”, ”.”
        ”—” and ”..” are forbidden

    Refer to:
    https://huggingface.co/docs/huggingface_hub/package_reference/utilities#huggingface_hub.utils.validate_repo_id
    """
    huggingface_validators.throw_error_on_invalid_identifier(platform_resource_identifier)
    if "/" not in platform_resource_identifier:
        msg = (
            f"The username should be part of the platform_resource_identifier for HuggingFace: "
            f"{username}/{platform_resource_identifier}. Please update the dataset "
            f"platform_resource_identifier."
        )
        # In general, it's allowed in HuggingFace to have a dataset name without namespace. This
        # is legacy: "The legacy GitHub datasets were added originally on our GitHub repository
        # and therefore don’t have a namespace on the Hub".
        # Any new dataset will therefore have a namespace. Since we're uploading a new dataset,
        # we should not accept a legacy name.
        raise ValueError(msg)

    namespace = platform_resource_identifier.split("/")[0]
    if username != namespace:
        msg = (
            f"The namespace (the first part of the platform_resource_identifier) should be "
            f"equal to the username, but {namespace} != {username}."
        )
        raise ValueError(msg)
