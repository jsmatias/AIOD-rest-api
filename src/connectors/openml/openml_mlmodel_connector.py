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
from database.model import field_length
from database.model.ai_resource.text import Text
from database.model.concept.aiod_entry import AIoDEntryCreate
from database.model.models_and_experiments.ml_model import MLModel

# from database.model.models_and_experiments.runnable_distribution import RunnableDistribution
from database.model.platform.platform_names import PlatformName
from database.model.resource_read_and_create import resource_create


class OpenMlMLModelConnector(ResourceConnectorById[MLModel]):
    """
    Openml does not allow gathering the records based on the last modified datetime. Instead,
    it does guarantee strictly ascending identifiers. This is the reason why the
    ResourceConnectorById is used.
    """

    @property
    def resource_class(self) -> type[MLModel]:
        return MLModel

    @property
    def platform_name(self) -> PlatformName:
        return PlatformName.openml

    def retry(self, identifier: int) -> SQLModel | RecordError:
        return self.fetch_record(identifier)

    def fetch_record(self, identifier: int) -> SQLModel | RecordError:
        url_mlmodel = f"https://www.openml.org/api/v1/json/flow/{identifier}"
        response = requests.get(url_mlmodel)
        if not response.ok:
            msg = response.json()["error"]["message"]
            return RecordError(
                identifier=str(identifier),
                error=f"Error while fetching flow from OpenML: '{msg}'.",
            )
        mlmodel_json = response.json()["flow"]

        pydantic_class = resource_create(MLModel)
        description = mlmodel_json["description"]
        if isinstance(description, list) and len(description) == 0:
            description = ""
        elif not isinstance(description, str):
            return RecordError(identifier=str(identifier), error="Description of unknown format.")
        if len(description) > field_length.LONG:
            text_break = " [...]"
            description = description[: field_length.LONG - len(text_break)] + text_break
        if description:
            description = Text(plain=description)
        # distribution = [
        #     RunnableDistribution(
        #         dependency=mlmodel_json["dependencies"]
        #         if "dependencies" in mlmodel_json else None,
        #         installation=mlmodel_json["installation_notes"]
        #         if "installation_notes" in mlmodel_json
        #         else None,
        #         content_url=mlmodel_json["binary_url"] if "binary_url" in mlmodel_json else None,
        #     )
        # ]
        return pydantic_class(
            aiod_entry=AIoDEntryCreate(
                status="published",
            ),
            platform_resource_identifier=identifier,
            platform=self.platform_name,
            name=mlmodel_json["name"],
            same_as=url_mlmodel,
            description=description,
            date_published=dateutil.parser.parse(mlmodel_json["upload_date"]),
            license=mlmodel_json["licence"] if "licence" in mlmodel_json else None,
            # distribution=distribution,
            is_accessible_for_free=True,
            # size=size,
            keyword=[tag for tag in mlmodel_json["tag"]] if "tag" in mlmodel_json else [],
            version=mlmodel_json["version"],
        )

    def fetch(self, offset: int, from_identifier: int) -> Iterator[SQLModel | RecordError]:
        url_mlmodel = (
            "https://www.openml.org/api/v1/json/flow/list/"
            f"limit/{self.limit_per_iteration}/offset/{offset}"
        )
        response = requests.get(url_mlmodel)
        if not response.ok:
            msg = response.json()["error"]["message"]
            yield RecordError(
                identifier=None,
                error=f"Error while fetching {url_mlmodel} from OpenML: '{msg}'.",
            )
            return

        try:
            mlmodel_summaries = response.json()["flows"]["flow"]
        except Exception as e:
            yield RecordError(identifier=None, error=e)
            return

        for summary in mlmodel_summaries:
            identifier = None
            try:
                identifier = summary["id"]
                if identifier < from_identifier:
                    yield RecordError(identifier=identifier, error="Id too low", ignore=True)
                if from_identifier is None or identifier >= from_identifier:
                    yield self.fetch_record(identifier)
            except Exception as e:
                yield RecordError(identifier=identifier, error=e)


def _as_int(v: str) -> int:
    as_float = float(v)
    if not as_float.is_integer():
        raise ValueError(f"The input should be an integer, but was a float: {v}")
    return int(as_float)
