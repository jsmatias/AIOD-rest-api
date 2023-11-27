import io
import json
import requests

from fastapi import UploadFile, HTTPException, status

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from database.model.dataset.dataset import Dataset


class ZenodoUploader:
    @property
    def base_url(self) -> str:
        return "https://zenodo.org/api/deposit/depositions"

    def handle_upload(self, engine: Engine, identifier: int, token: str, file: UploadFile):
        """
        Method to upload content to the Zenodo platform.
        """
        with Session(engine) as session:
            dataset = self._get_resource(session, identifier)
            platform_resource_id = dataset.platform_resource_identifier
            platform_name = dataset.platform
            metadata = self._generate_metadata_file(dataset)

            if platform_resource_id is not None:
                if platform_name == "zenodo":
                    repo_id = platform_resource_id.split(":")[-1]
                    current_zenodo_metadata = self._get_metadata_from_zenodo(repo_id, token)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Platform name {platform_name} conflict! "
                        "Verify that the platform name in the metadata is either 'zenodo' or empty",
                    )
            else:
                current_zenodo_metadata = self._create_repo(token, metadata)
                repo_id = current_zenodo_metadata["id"]
                dataset.platform = "zenodo"
                dataset.platform_resource_identifier = f"zenodo.org:{repo_id}"

            self._update_zenodo_metadata(repo_id, token, metadata)

            repo_url = current_zenodo_metadata["links"]["bucket"]
            self._upload_file(repo_url, token, file)

            # TODO: Include an option (as a parameter) to publish the dataset on zenodo.
            # This requires the field resource_type in the metadata.
            # The string "dataset" isn't recognised as a valid resource_type
            # URL to publish: f"{repo_url}/{repo_id}/actions/publish"

            new_zenodo_metadata = self._get_metadata_from_zenodo(repo_id, token)
            new_file_metadata = [
                file
                for file in new_zenodo_metadata["files"]
                if file not in current_zenodo_metadata["files"]
            ][0]
            distribution = self._generate_distribution(new_file_metadata)

            self._store_resource_updated(session, dataset, distribution)

            return dataset.identifier

    def _get_resource(self, session: Session, identifier: int) -> Dataset:
        """
        Returns a dataset identified by its AIoD identifier.
        """
        query = select(Dataset).where(Dataset.identifier == identifier)

        dataset = session.scalars(query).first()
        if not dataset or dataset.date_deleted is not None:
            name = f"Dataset '{identifier}'"
            msg = "not found in the database"
            msg += "." if not dataset else ", because it was deleted."

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} {msg}")
        return dataset

    def _create_repo(self, token: str, metadata: dict) -> dict:
        """
        Creates an empty repo with some metadata on Zenodo.
        """
        params = {"access_token": token}
        try:
            res = requests.post(
                self.base_url,
                params=params,
                json={"metadata": metadata},
            )
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_201_CREATED:
            msg = "Error creating a new repo on zenodo. Zenodo api returned a http error:"
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

        return res.json()

    def _get_metadata_from_zenodo(self, repo_id: str, token: str) -> dict:
        """
        Get metadata of the dataset identified by its identifier `repo_id` from Zenodo.
        """
        params = {"access_token": token}
        try:
            res = requests.get(f"{self.base_url}/{repo_id}", params=params)
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_200_OK:
            msg = "Error retrieving information from zenodo. Zenodo api returned a http error:"
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

        return res.json()

    def _update_zenodo_metadata(self, repo_id: str, token: str, metadata: dict) -> None:
        """
        Updates the zenodo repo with some metadata.
        """
        headers = {"Content-Type": "application/json"}
        try:
            res = requests.put(
                f"{self.base_url}/{repo_id}",
                params={"access_token": token},
                data=json.dumps({"metadata": metadata}),
                headers=headers,
            )
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_200_OK:
            msg = "Error uploading metadata to zenodo. Zenodo api returned a http error:"
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

    def _upload_file(self, repo_url: str, token: str, file: UploadFile) -> None:
        """
        Uploads a file to zenodo using a bucket url where the files are stored.
        """
        params = {"access_token": token}
        try:
            res = requests.put(
                f"{repo_url}/{file.filename}", data=io.BufferedReader(file.file), params=params
            )
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_201_CREATED:
            msg = "Error uploading a file to zenodo. Zenodo api returned a http error:"
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

    def _generate_metadata_file(self, dataset: Dataset) -> dict:
        """
        Generates metadata as a dictionary based on the data from the dataset model.
        """
        metadata = {
            "title": dataset.name,
            "description": f"{dataset.description.plain if dataset.description else ''}.\n"
            "Created from AIOD platform",
            "creators": [
                {"name": f"{creator.name}", "affiliation": ""} for creator in dataset.creator
            ],
            "keywords": [kw.name for kw in dataset.keyword],
            "method": dataset.measurement_technique or "",
            "access_right": f"{'open' if dataset.is_accessible_for_free else 'closed'}",
            # TODO: include licence in the right format.
            # "license": dataset.license.name if dataset.license else "cc-zero",
        }

        return metadata

    def _generate_distribution(self, file_metadata: dict) -> dict:
        """
        Generated the a distribution dictionary from a dictonary response.
        """
        distribution = {
            "platform": "zenodo",
            "platform_resource_identifier": file_metadata["id"],
            "checksum": file_metadata["checksum"],
            "content_url": file_metadata["links"]["download"],
            "content_size_kb": file_metadata["filesize"],
            "name": file_metadata["filename"],
        }

        return distribution

    def _store_resource_updated(self, session: Session, resource: Dataset, distribution_dict: dict):
        """
        Updates the resource data appending the content information as a distribution.
        """

        try:
            # Hack to get the right DistributionORM class (for each class, such as Dataset
            # and Publication, there is a different DistributionORM table).
            dist = resource.RelationshipConfig.distribution.deserializer.clazz  # type: ignore
            distribution = dist(dataset=resource, **distribution_dict)
            aiod_dist_names = [dist.name for dist in resource.distribution]

            # Using name instead of if as the URI for the file is based on the file's name.
            if distribution.name in aiod_dist_names:
                idx = aiod_dist_names.index(distribution.name)
                resource.distribution[idx] = distribution
            else:
                resource.distribution.append(distribution)

            session.merge(resource)
            session.commit()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Dataset metadata could not be updated with distribution on AIoD database.",
            ) from exc


def _wrap_exception_as_http_exception(exc: Exception):
    if isinstance(exc, HTTPException):
        return exc

    exception = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=(
            "Unexpected exception while processing your request. "
            "Please contact the maintainers: "
            f"{exc}"
        ),
    )
    return exception
