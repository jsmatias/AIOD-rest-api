from datetime import datetime
from typing import Iterator, Tuple

import dateutil.parser
import requests
import xmltodict
from sickle import Sickle
from sqlmodel import SQLModel
from starlette import status

from connectors.abstract.resource_connector_by_date import ResourceConnectorByDate
from connectors.record_error import RecordError
from connectors.resource_with_relations import ResourceWithRelations
from database.model import field_length
from database.model.agent.contact import Contact
from database.model.ai_asset.distribution import Distribution
from database.model.ai_resource.text import Text
from database.model.concept.aiod_entry import AIoDEntryCreate
from database.model.dataset.dataset import Dataset
from database.model.platform.platform_names import PlatformName
from database.model.resource_read_and_create import resource_create


DATE_FORMAT = "%Y-%m-%d"


class ZenodoDatasetConnector(ResourceConnectorByDate[Dataset]):
    @property
    def resource_class(self) -> type[Dataset]:
        return Dataset

    @property
    def platform_name(self) -> PlatformName:
        return PlatformName.zenodo

    def retry(self, _id: int) -> ResourceWithRelations[Dataset] | RecordError:
        """
        This function fetches only one record from Zenodo using the Rest API instead of
        the OAI-PMH one. When querying using the OAI protocol, we always receive all the
        records, making it really inefficient to filter through all of them until we get
        the one we want. Apart from using different protocols, they also employ different
        serialization methods. The Rest API uses JSON, while OAI uses XML, which is why the
        code shows no similarities.
        """

        raise NotImplementedError(
            "Currently not implemented. See git history for an earlier "
            "implementation, that needs to be brought up-to-date (ideally "
            "using the same code as fetch)."
        )

    @staticmethod
    def _error_msg_bad_format(field) -> str:
        return f"Error while fetching record info: bad format {field}"

    @staticmethod
    def _dataset_from_record(
        identifier: str, record: dict
    ) -> ResourceWithRelations[Dataset] | RecordError:
        error_fmt = ZenodoDatasetConnector._error_msg_bad_format
        if isinstance(record["creators"]["creator"], list):
            creator_names = [item["creatorName"]["#text"] for item in record["creators"]["creator"]]
        elif isinstance(record["creators"]["creator"]["creatorName"]["#text"], str):
            creator_names = [record["creators"]["creator"]["creatorName"]["#text"]]
        else:
            error_fmt("")
            return RecordError(identifier=identifier, error=error_fmt("creator"))

        creators = []
        pydantic_class_contact = resource_create(Contact)
        for name in creator_names:
            creators.append(pydantic_class_contact(name=name))

        if isinstance(record["titles"]["title"], str):
            title = record["titles"]["title"]
        else:
            return RecordError(identifier=identifier, error=error_fmt("title"))
        if len(title) > field_length.NORMAL:
            text_break = " [...]"
            title = title[: field_length.NORMAL - len(text_break)] + text_break

        number_str = identifier.rsplit("/", 1)[-1]
        id_number = "".join(filter(str.isdigit, number_str))
        same_as = f"https://zenodo.org/api/records/{id_number}"

        description_raw = record["descriptions"]["description"]
        if isinstance(description_raw, list):
            (description,) = [
                e.get("#text") for e in description_raw if e.get("@descriptionType") == "Abstract"
            ]
        elif description_raw["@descriptionType"] == "Abstract":
            description = description_raw["#text"]
        else:
            return RecordError(identifier=identifier, error=error_fmt("description"))
        if len(description) > field_length.LONG:
            text_break = " [...]"
            description = description[: field_length.LONG - len(text_break)] + text_break
        if description:
            description = Text(plain=description)

        date_published = None
        date_raw = record["dates"]["date"]
        if isinstance(date_raw, list):
            (description,) = [e.get("#text") for e in date_raw if e.get("@dateType") == "Issued"]
        elif date_raw["@dateType"] == "Issued":
            date_string = date_raw["#text"]
            date_published = datetime.strptime(date_string, DATE_FORMAT)
        else:
            return RecordError(identifier=identifier, error=error_fmt("date_published"))

        publisher = None
        if "publisher" in record:
            if isinstance(record["publisher"], str):
                publisher = record["publisher"]
            else:
                return RecordError(identifier=identifier, error=error_fmt("publisher"))

        license_ = None
        if "rightsList" in record:
            if isinstance(record["rightsList"]["rights"], list):
                license_ = record["rightsList"]["rights"][0]["#text"]
            elif isinstance(record["rightsList"]["rights"]["#text"], str):
                license_ = record["rightsList"]["rights"]["#text"]
            else:
                return RecordError(identifier=identifier, error=error_fmt("license"))

        keywords = []
        if "subjects" in record:
            if isinstance(record["subjects"]["subject"], str):
                keywords = [record["subjects"]["subject"]]
            elif isinstance(record["subjects"]["subject"], list):
                keywords = [item for item in record["subjects"]["subject"] if isinstance(item, str)]
            else:
                return RecordError(identifier=identifier, error=error_fmt("keywords"))

        response = requests.get(f"https://zenodo.org/api/records/{id_number}/files")
        if response.status_code == status.HTTP_200_OK:
            entries = response.json()["entries"]
            distributions = [
                Distribution(
                    name=entry["key"],
                    content_url=entry["links"]["content"],
                    encoding_format=entry["mimetype"],
                    checksum_algorithm=entry["checksum"].split(":")[0]
                    if "checksum" in entry
                    else None,
                    checksum=entry["checksum"].split(":")[1] if "checksum" in entry else None,
                )
                for entry in entries
            ]
        elif response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_410_GONE):
            distributions = []  # Private files, or deleted files
        else:
            response.raise_for_status()

        pydantic_class = resource_create(Dataset)
        dataset = pydantic_class(
            aiod_entry=AIoDEntryCreate(status="published"),
            platform="zenodo",
            platform_resource_identifier=identifier,
            name=title,
            same_as=same_as,
            description=description,
            date_published=date_published,
            publisher=publisher,
            license=license_,
            keyword=keywords,
            distribution=distributions,
        )

        return ResourceWithRelations[pydantic_class](  # type:ignore
            resource=dataset, resource_ORM_class=Dataset, related_resources={"creator": creators}
        )

    @staticmethod
    def _resource_type(record) -> str | None:
        """Cheap check before parsing the complete XML."""
        xml_string = record.raw
        start = xml_string.find('<resourceType resourceTypeGeneral="')
        if start != -1:
            start += len('<resourceType resourceTypeGeneral="')
            end = xml_string.find('"', start)
            if end != -1:
                return xml_string[start:end]
        return None

    def fetch(
        self, from_incl: datetime, to_excl: datetime
    ) -> Iterator[Tuple[datetime | None, SQLModel | ResourceWithRelations[SQLModel] | RecordError]]:
        sickle = Sickle("https://zenodo.org/oai2d")
        records = sickle.ListRecords(
            **{
                "metadataPrefix": "oai_datacite",
                "from": from_incl.isoformat(),
                "until": to_excl.isoformat(),
            }
        )

        for record in records:
            id_ = None
            datetime_ = None
            resource_type = ZenodoDatasetConnector._resource_type(record)
            if resource_type is None:
                yield datetime_, RecordError(
                    identifier=id_, error="Resource type could not be determined"
                )
            if resource_type == "Dataset":
                try:
                    xml_string = record.raw
                    xml_dict = xmltodict.parse(xml_string)
                    id_ = xml_dict["record"]["header"]["identifier"]
                    if id_.startswith("oai:"):
                        id_ = id_.replace("oai:", "")
                    datetime_ = dateutil.parser.parse(xml_dict["record"]["header"]["datestamp"])
                    resource = xml_dict["record"]["metadata"]["oai_datacite"]["payload"]["resource"]
                    yield datetime_, self._dataset_from_record(id_, resource)
                except Exception as e:
                    yield datetime_, RecordError(identifier=id_, error=e)
            else:
                yield datetime_, RecordError(identifier=id_, error="Wrong type", ignore=True)
