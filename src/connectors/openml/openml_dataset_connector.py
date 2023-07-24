"""
This module knows how to load an OpenML object based on its AIoD implementation,
and how to convert the OpenML response to some agreed AIoD format.
"""

from typing import Iterator, List

import dateutil.parser
import requests
from fastapi import HTTPException
from sqlmodel import SQLModel


from connectors.abstract.resource_connector_by_id import ResourceConnectorById
from database.model.dataset.data_download import DataDownload
from database.model.dataset.dataset import Dataset
from database.model.resource import resource_create
from database.model.platform.platform_names import PlatformName
from connectors.record_error import RecordError


class OpenMlDatasetConnector(ResourceConnectorById[Dataset]):
    """ "
    Openml orders its records with a numeric id in ascendent order but does not allow
    gather them from a certain date. This is the reason why the ResourceConnectorById
    is needed
    """

    @property
    def resource_class(self) -> type[Dataset]:
        return Dataset

    @property
    def platform_name(self) -> PlatformName:
        return PlatformName.openml

    def retry(self, _id: int) -> SQLModel:
        url_data = f"https://www.openml.org/api/v1/json/data/{_id}"
        response = requests.get(url_data)
        if not response.ok:
            code = response.status_code
            if code == 412 and response.json()["error"]["message"] == "Unknown dataset":
                code = 404
            msg = response.json()["error"]["message"]

            return RecordError(
                platform="openml",
                _id=str(_id),
                error=f"Error while fetching data from OpenML: '{msg}'.",
                type="dataset",
            )
        dataset_json = response.json()["data_set_description"]

        # Here we can format the response into some standardized way, maybe this includes some
        # dataset characteristics. These need to be retrieved separately from OpenML:
        url_qual = f"https://www.openml.org/api/v1/json/data/qualities/{_id}"
        response = requests.get(url_qual)
        if not response.ok:
            msg = response.json()["error"]["message"]
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error while fetching data qualities from OpenML: '{msg}'.",
            )

        qualities_json = {
            quality["name"]: quality["value"]
            for quality in response.json()["data_qualities"]["quality"]
        }
        pydantic_class = resource_create(Dataset)
        return pydantic_class(
            platform=self.platform_name,
            platform_identifier=_id,
            name=dataset_json["name"],
            same_as=url_data,
            description=dataset_json["description"],
            date_published=dateutil.parser.parse(dataset_json["upload_date"]),
            date_modified=dateutil.parser.parse(dataset_json["processing_date"]),
            distributions=[
                DataDownload(
                    content_url=dataset_json["url"], encoding_format=dataset_json["format"]
                )
            ],
            size=_as_int(qualities_json["NumberOfInstances"]),
            is_accessible_for_free=True,
            keywords=[tag for tag in dataset_json["tag"]],
            license=dataset_json["licence"] if "licence" in dataset_json else None,
            version=dataset_json["version"],
            alternate_names=[],
            citations=[],
            is_part=[],
            has_parts=[],
            measured_values=[],
        )

    def check_valid_id(self, from_id: int, to_id: int) -> List[int]:
        url = f"https://www.openml.org/api/v1/json/data/list/data_id/{','.join(map(str, range(from_id, to_id)))}"  # noqa E501
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            existing_ids = [int(item["did"]) for item in data.get("data", {}).get("dataset", [])]
            return existing_ids
        elif response.status_code == 412:
            return [-1]
        else:
            raise ValueError()

    def fetch(self, from_id: int, to_id: int) -> Iterator[SQLModel | RecordError]:
        valid_ids = self.check_valid_id(from_id, to_id)
        if valid_ids[0] == -1:
            return RecordError(
                _id=str(from_id),
                platform="openml",
                type="datset",
                error="No more datasets to retrieve",
            )
        for _id in valid_ids:
            try:
                dataset = self.retry(_id)
                yield dataset
            except Exception as e:
                yield RecordError(_id=str(_id), platform="openml", type="dataset", error=str(e))


def _as_int(v: str) -> int:
    as_float = float(v)
    if not as_float.is_integer():
        raise ValueError(f"The input should be an integer, but was a float: {v}")
    return int(as_float)
