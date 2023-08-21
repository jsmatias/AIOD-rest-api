"""
This module knows how to load an OpenML object based on its AIoD implementation,
and how to convert the OpenML response to some agreed AIoD format.
"""

from typing import Iterator

import dateutil.parser
import requests
from sqlmodel import SQLModel

from connectors.abstract.resource_connector_by_id import ResourceConnectorById
from connectors.record_error import RecordError
from database.model.ai_asset.distribution import Distribution
from database.model.concept.aiod_entry import AIoDEntryCreate
from database.model.dataset.dataset import Dataset
from database.model.dataset.size import Size
from database.model.platform.platform_names import PlatformName
from database.model.resource_read_and_create import resource_create


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

    def retry(self, identifier: int) -> SQLModel | RecordError:
        url_qual = f"https://www.openml.org/api/v1/json/data/qualities/{identifier}"
        response = requests.get(url_qual)
        if not response.ok:
            msg = response.json()["error"]["message"]
            return RecordError(
                identifier=str(identifier),
                error=f"Error while fetching data from OpenML: '{msg}'.",
            )
        qualities = response.json()["data_qualities"]["quality"]
        return self.fetch_record(identifier, qualities)

    def fetch_record(
        self, identifier: int, qualities: list[dict[str, str]]
    ) -> SQLModel | RecordError:
        url_data = f"https://www.openml.org/api/v1/json/data/{identifier}"
        response = requests.get(url_data)
        if not response.ok:
            msg = response.json()["error"]["message"]
            return RecordError(
                identifier=str(identifier),
                error=f"Error while fetching data from OpenML: '{msg}'.",
            )
        dataset_json = response.json()["data_set_description"]

        qualities_json = {quality["name"]: quality["value"] for quality in qualities}
        pydantic_class = resource_create(Dataset)
        return pydantic_class(
            aiod_entry=AIoDEntryCreate(
                platform=self.platform_name,
                platform_identifier=identifier,
            ),
            name=dataset_json["name"],
            same_as=url_data,
            description=dataset_json["description"],
            date_published=dateutil.parser.parse(dataset_json["upload_date"]),
            distribution=[
                Distribution(
                    content_url=dataset_json["url"], encoding_format=dataset_json["format"]
                )
            ],
            size=Size(value=_as_int(qualities_json["NumberOfInstances"]), unit="instances"),
            is_accessible_for_free=True,
            keyword=[tag for tag in dataset_json["tag"]],
            license=dataset_json["licence"] if "licence" in dataset_json else None,
            version=dataset_json["version"],
        )

    def fetch(self, offset: int, from_identifier: int) -> Iterator[SQLModel | RecordError]:
        url_data = (
            "https://www.openml.org/api/v1/json/data/list/"
            f"limit/{self.limit_per_iteration}/offset/{offset}"
        )
        response = requests.get(url_data)
        if not response.ok:
            msg = response.json()["error"]["message"]
            yield RecordError(
                identifier=None,
                error=f"Error while fetching {url_data} from OpenML: '{msg}'.",
            )
            return

        try:
            dataset_summaries = response.json()["data"]["dataset"]
        except Exception as e:
            yield RecordError(identifier=None, error=e)
            return

        for summary in dataset_summaries:
            identifier = None
            try:
                identifier = summary["did"]
                qualities = summary["quality"]
                yield self.fetch_record(identifier, qualities)
            except Exception as e:
                yield RecordError(identifier=identifier, error=e)


def _as_int(v: str) -> int:
    as_float = float(v)
    if not as_float.is_integer():
        raise ValueError(f"The input should be an integer, but was a float: {v}")
    return int(as_float)
