from datetime import datetime, date
from typing import Iterator, Tuple

import requests
import xmltodict
from sickle import Sickle
from sqlmodel import SQLModel

from connectors.abstract.resource_connector_by_date import ResourceConnectorByDate
from connectors.record_error import RecordError
from connectors.resource_with_relations import ResourceWithRelations
from database.model.dataset.dataset import Dataset
from database.model.general.keyword import Keyword
from database.model.general.license import License
from database.model.platform.platform_names import PlatformName

DATE_FORMAT = "%Y-%m-%d"


class ZenodoDatasetConnector(ResourceConnectorByDate[Dataset]):
    @property
    def resource_class(self) -> type[Dataset]:
        return Dataset

    @property
    def platform_name(self) -> PlatformName:
        return PlatformName.zenodo

    def retry(self, _id: int) -> Dataset | RecordError:
        """
        This function fetches only one record from Zenodo using the Rest API instead of
        the OAI-PMH one. When querying using the OAI protocol, we always receive all the
        records, making it really inefficient to filter through all of them until we get
        the one we want. Apart from using different protocols, they also employ different
        serialization methods. The Rest API uses JSON, while OAI uses XML, which is why the
        code shows no similarities.
        """

        response = requests.get(f"https://zenodo.org/api/records/{_id}")
        if not response.ok:
            msg = response.json()["error"]["message"]
            return RecordError(
                identifier=str(_id),
                error=f"Error while fetching data from Zenodo: '{msg}'.",
            )

        record = response.json()
        creators_list = [item["name"] for item in record["metadata"]["creators"]]
        creator = "; ".join(creators_list)  # TODO change field to an array
        return Dataset(
            platform="zenodo",
            platform_identifier=_id,
            date_published=record.get("created"),
            name=record.get("metadata").get("title"),
            description=record.get("metadata").get("description"),
            creator=creator,
            publisher="Zenodo",
            license=License(name=record.get("metadata").get("license").get("id")),
            keywords=[Keyword(name=k) for k in record.get("metadata").get("keywords")],
        )

    @staticmethod
    def _error_msg_bad_format(field) -> str:
        return f"Error while fetching record info: bad format {field}"

    @staticmethod
    def _dataset_from_record(identifier: str, record: dict) -> Dataset | RecordError:
        error_fmt = ZenodoDatasetConnector._error_msg_bad_format
        if isinstance(record["creators"]["creator"], list):
            creators_list = [item["creatorName"] for item in record["creators"]["creator"]]
            creator = "; ".join(creators_list)  # TODO change field to an array
        elif isinstance(record["creators"]["creator"]["creatorName"], str):
            creator = record["creators"]["creator"]["creatorName"]
        else:
            error_fmt("")
            return RecordError(identifier=identifier, error=error_fmt("creator"))

        if isinstance(record["titles"]["title"], str):
            title = record["titles"]["title"]
        else:
            return RecordError(identifier=identifier, error=error_fmt("title"))
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

        date_published = None
        date_raw = record["dates"]["date"]
        if isinstance(date_raw, list):
            (description,) = [e.get("#text") for e in date_raw if e.get("@dateType") == "Issued"]
        elif date_raw["@dateType"] == "Issued":
            date_string = date_raw["#text"]
            date_published = datetime.strptime(date_string, DATE_FORMAT)
        else:
            return RecordError(identifier=identifier, error=error_fmt("date_published"))

        if isinstance(record["publisher"], str):
            publisher = record["publisher"]
        else:
            return RecordError(identifier=identifier, error=error_fmt("publisher"))

        if isinstance(record["rightsList"]["rights"], list):
            license_ = record["rightsList"]["rights"][0]["@rightsURI"]
        elif isinstance(record["rightsList"]["rights"]["@rightsURI"], str):
            license_ = record["rightsList"]["rights"]["@rightsURI"]
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

        dataset = Dataset(
            platform="zenodo",
            platform_identifier=identifier,
            name=title[:150],
            same_as=same_as,
            creator=creator[
                :150
            ],  # TODO not enough characters for creator list, change to array or allow more length
            description=description[:500],
            date_published=date_published,
            publisher=publisher,
            license=License(name=license_) if license_ is not None else None,
            keywords=[Keyword(name=k) for k in keywords],
        )
        return dataset

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
    ) -> Iterator[Tuple[date | None, SQLModel | ResourceWithRelations[SQLModel] | RecordError]]:
        sickle = Sickle("https://zenodo.org/oai2d")
        records = sickle.ListRecords(
            **{
                "metadataPrefix": "oai_datacite",
                "from": from_incl.isoformat(),
                "until": to_excl.isoformat(),
            }
        )

        while record := next(records, None):
            id_ = None
            datetime_ = None
            resource_type = ZenodoDatasetConnector._resource_type(record)
            if resource_type is None:
                yield datetime_, RecordError(
                    identifier=id_, error="Resource type could not be " "determined"
                )
            if resource_type == "Dataset":
                try:
                    xml_string = record.raw
                    xml_dict = xmltodict.parse(xml_string)
                    id_ = xml_dict["record"]["header"]["identifier"]
                    if id_.startswith("oai:"):
                        id_ = id_.replace("oai:", "")
                    datetime_ = xml_dict["record"]["header"]["datestamp"]
                    resource = xml_dict["record"]["metadata"]["oai_datacite"]["payload"]["resource"]
                    yield datetime_, self._dataset_from_record(id_, resource)
                except Exception as e:
                    yield datetime_, RecordError(identifier=id_, error=e)
