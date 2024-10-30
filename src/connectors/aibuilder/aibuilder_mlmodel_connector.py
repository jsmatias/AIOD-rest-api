"""AIBuilder MLModel Connector
This module knows how to load an AIBuilder object from their API and to
convert the AIBuilder response to the AIoD MLModel format.
"""

#import dateutil.parser
#import requests
#import logging

#from requests.exceptions import HTTPError
#
#from typing import Iterator, Any

#
#
#from database.model import field_length
#from database.model.ai_resource.text import Text
#from database.model.concept.aiod_entry import AIoDEntryCreate


#from database.model.agent.contact import Contact
#from database.model.models_and_experiments.runnable_distribution import RunnableDistribution
#
#from database.model.resource_read_and_create import resource_create
#

from sqlmodel import SQLModel

from database.model.models_and_experiments.ml_model import MLModel
from database.model.platform.platform_names import PlatformName

from connectors.abstract.resource_connector_by_id import ResourceConnectorByDate
from connectors.resource_with_relations import ResourceWithRelations
from connectors.record_error import RecordError

class AIBuilderMLModelConnector(ResourceConnectorByDate[MLModel]):
    @property
    def resource_class(self) -> type[MLModel]:
        return MLModel

    @property
    def platform_name(self) -> PlatformName:
        return PlatformName.aibuilder

    def retry(self, identifier: int) -> ResourceWithRelations[SQLModel] | RecordError:
        return self.fetch_record(identifier)








    def fetch_record(self, identifier: int) -> ResourceWithRelations[MLModel] | RecordError:
        url_mlmodel = f"https://www.openml.org/api/v1/json/flow/{identifier}"
        response = requests.get(url_mlmodel)
        if not response.ok:
            msg = response.json()["error"]["message"]
            return RecordError(
                identifier=str(identifier),
                error=f"Error while fetching flow from OpenML: '{msg}'.",
            )
        mlmodel_json = response.json()["flow"]

        description_or_error = _description(mlmodel_json, identifier)
        if isinstance(description_or_error, RecordError):
            return description_or_error
        description = description_or_error

        distribution = _distributions(mlmodel_json)

        openml_creator = _as_list(mlmodel_json.get("creator", None))
        openml_contributor = _as_list(mlmodel_json.get("contributor", None))
        pydantic_class_contact = resource_create(Contact)
        creator_names = [
            pydantic_class_contact(name=name) for name in openml_creator + openml_contributor
        ]

        tags = _as_list(mlmodel_json.get("tag", None))

        pydantic_class = resource_create(MLModel)
        mlmodel = pydantic_class(
            aiod_entry=AIoDEntryCreate(
                status="published",
            ),
            platform_resource_identifier=identifier,
            platform=self.platform_name,
            name=mlmodel_json["name"],
            same_as=url_mlmodel,
            description=description,
            date_published=dateutil.parser.parse(mlmodel_json["upload_date"]),
            license=mlmodel_json.get("licence", None),
            distribution=distribution,
            is_accessible_for_free=True,
            keyword=[tag for tag in tags] if tags else [],
            version=mlmodel_json["version"],
        )

        return ResourceWithRelations[pydantic_class](  # type:ignore
            resource=mlmodel,
            resource_ORM_class=MLModel,
            related_resources={"creator": creator_names},
        )

    def fetch(
        self, offset: int, from_identifier: int
    ) -> Iterator[ResourceWithRelations[SQLModel] | RecordError]:
        url_mlmodel = (
            "https://www.openml.org/api/v1/json/flow/list/"
            f"limit/{self.limit_per_iteration}/offset/{offset}"
        )
        response = requests.get(url_mlmodel)

        if not response.ok:
            status_code = response.status_code
            msg = response.json()["error"]["message"]
            err_msg = f"Error while fetching {url_mlmodel} from OpenML: ({status_code}) {msg}"
            logging.error(err_msg)
            err = HTTPError(err_msg)
            yield RecordError(identifier=None, error=err)
            return

        try:
            mlmodel_summaries = response.json()["flows"]["flow"]
        except Exception as e:
            yield RecordError(identifier=None, error=e)
            return

        for summary in mlmodel_summaries:
            identifier = None
            # ToDo: discuss how to accommodate pipelines. Excluding sklearn pipelines for now.
            # Note: weka doesn't have a standard method to define pipeline.
            # There are no mlr pipelines in OpenML.
            identifier = summary["id"]
            if "sklearn.pipeline" not in summary["name"]:
                try:
                    if identifier < from_identifier:
                        yield RecordError(identifier=identifier, error="Id too low", ignore=True)
                    if from_identifier is None or identifier >= from_identifier:
                        yield self.fetch_record(identifier)
                except Exception as e:
                    yield RecordError(identifier=identifier, error=e)
            else:
                yield RecordError(identifier=identifier, error="Sklearn pipeline not processed!")


def _description(mlmodel_json: dict[str, Any], identifier: int) -> Text | None | RecordError:
    description = (
        mlmodel_json["full_description"]
        if mlmodel_json.get("full_description", None)
        else mlmodel_json.get("description", None)
    )
    if isinstance(description, type(None)):
        return None
    if isinstance(description, list) and len(description) == 0:
        return None
    elif not isinstance(description, str):
        return RecordError(identifier=str(identifier), error="Description of unknown format.")
    if len(description) > field_length.LONG:
        text_break = " [...]"
        description = description[: field_length.LONG - len(text_break)] + text_break
    if description:
        return Text(plain=description)
    return None


def _distributions(mlmodel_json) -> list[RunnableDistribution]:
    if (
        (mlmodel_json.get("installation_notes") is None)
        and (mlmodel_json.get("dependencies") is None)
        and (mlmodel_json.get("binary_url") is None)
    ):
        return []
    return [
        RunnableDistribution(
            dependency=mlmodel_json.get("dependencies", None),
            installation=mlmodel_json.get("installation_notes", None),
            content_url=mlmodel_json.get("binary_url", None),
        )
    ]


def _as_list(value: Any | list[Any]) -> list[Any]:
    """Wrap it with a list, if it is not a list"""
    if not value:
        return []
    if not isinstance(value, list):
        return [value]
    return value
