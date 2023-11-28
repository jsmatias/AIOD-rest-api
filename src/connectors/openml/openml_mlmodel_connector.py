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

from database.model.agent.contact import Contact
from database.model.models_and_experiments.runnable_distribution import RunnableDistribution
from database.model.platform.platform_names import PlatformName
from database.model.resource_read_and_create import resource_create
from connectors.resource_with_relations import ResourceWithRelations


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

        pydantic_class = resource_create(MLModel)
        description = (
            mlmodel_json["full_description"]
            if "full_description" in mlmodel_json
            else mlmodel_json["description"]
        )
        if isinstance(description, list) and len(description) == 0:
            description = ""
        elif not isinstance(description, str):
            return RecordError(identifier=str(identifier), error="Description of unknown format.")
        if len(description) > field_length.LONG:
            text_break = " [...]"
            description = description[: field_length.LONG - len(text_break)] + text_break
        if description:
            description = Text(plain=description)
        if (
            "dependencies" not in mlmodel_json
            and "installation_notes" not in mlmodel_json
            and "binary_url" not in mlmodel_json
        ):
            distribution = []
        else:
            distribution = [
                RunnableDistribution(
                    dependency=mlmodel_json.get("dependencies", None),
                    installation=mlmodel_json.get("installation_notes", None),
                    content_url=mlmodel_json.get("binary_url", None),
                )
            ]

        openml_creator = mlmodel_json.get("creator", None)
        openml_creator = (
            [openml_creator]
            if isinstance(openml_creator, str) and openml_creator
            else openml_creator
        )
        openml_contributor = mlmodel_json.get("contributor", None)
        openml_contributor = (
            [openml_contributor]
            if isinstance(openml_contributor, str) and openml_contributor
            else openml_contributor
        )

        creator_names = []
        pydantic_class_contact = resource_create(Contact)
        if openml_creator or openml_contributor:
            for name in openml_creator + openml_contributor:
                creator_names.append(pydantic_class_contact(name=name))

        tags = mlmodel_json.get("tag", None)
        tags = [tags] if isinstance(tags, str) and tags else tags

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
            # ToDo: dicuss how to accomodate pipelines. Excluding sklearn pipelines for now.
            # Note: weka doesn't have a standard method to define pipeline.
            # There are no mlr pipelines in OpenML.
            if "sklearn.pipeline" not in summary["name"]:
                try:
                    identifier = summary["id"]

                    if identifier < from_identifier:
                        yield RecordError(identifier=identifier, error="Id too low", ignore=True)
                    if from_identifier is None or identifier >= from_identifier:
                        yield self.fetch_record(identifier)
                except Exception as e:
                    yield RecordError(identifier=identifier, error=e)
