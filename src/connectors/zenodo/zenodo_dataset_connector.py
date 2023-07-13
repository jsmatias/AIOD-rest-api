from datetime import datetime
import logging
from typing import Iterator
import requests
from connectors.record_error import RecordError
from sickle import Sickle
import xmltodict

from connectors.abstract.resource_connector_by_date import ResourceConnectorByDate
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

    def retry(self, id: str) -> Dataset:
        """Retrieve information of the resource identified by id"""
        record = requests.get(f"https://zenodo.org/api/records/{id}").json()

        creators_list = [item["name"] for item in record["metadata"]["creators"]]
        creator = "; ".join(creators_list)  # TODO change field to an array
        return Dataset(
            platform="zenodo",
            platform_identifier=id,
            date_published=record.get("created"),
            name=record.get("metadata").get("title"),
            description=record.get("metadata").get("description"),
            creator=creator,
            publisher="Zenodo",
            license=License(name=record.get("metadata").get("license").get("id")),
            keywords=[Keyword(name=k) for k in record.get("metadata").get("keywords")],
        )

    def _get_record_dictionary(self, record):
        xml_string = record.raw
        xml_dict = xmltodict.parse(xml_string)
        id = xml_dict["record"]["header"]["identifier"]
        if id.startswith("oai:"):
            id = id.replace("oai:", "")
        resource = xml_dict["record"]["metadata"]["oai_datacite"]["payload"]["resource"]
        return id, resource

    def _bad_record_format(self, dataset_id, field):
        logging.error(
            f"Error while fetching record info for dataset {dataset_id}: bad format {field}"
        )

    def _dataset_from_record(self, record_raw) -> Dataset | RecordError:
        id_, record = self._get_record_dictionary(record_raw)
        if isinstance(record["creators"]["creator"], list):
            creators_list = [item["creatorName"] for item in record["creators"]["creator"]]
            creator = "; ".join(creators_list)  # TODO change field to an array
        elif isinstance(record["creators"]["creator"]["creatorName"], str):
            creator = record["creators"]["creator"]["creatorName"]
        else:
            self._bad_record_format(id_, "creator")
            return RecordError(
                id=id_, platform="zenodo", type="dataset", error="error decoding creator"
            )

        if isinstance(record["titles"]["title"], str):
            title = record["titles"]["title"]
        else:
            self._bad_record_format(id_, "title")
            return RecordError(
                id=id_, platform="zenodo", type="dataset", error="error decoding title"
            )
        number_str = id_.rsplit("/", 1)[-1]
        idNumber = "".join(filter(str.isdigit, number_str))
        same_as = f"https://zenodo.org/api/records/{idNumber}"

        description_raw = record["descriptions"]["description"]
        if isinstance(description_raw, list):
            (description,) = [
                e.get("#text") for e in description_raw if e.get("@descriptionType") == "Abstract"
            ]
        elif description_raw["@descriptionType"] == "Abstract":
            description = description_raw["#text"]
        else:
            self._bad_record_format(id_, "description")
            return RecordError(
                id=id_, platform="zenodo", type="dataset", error="error decoding description"
            )

        date_published = None
        date_raw = record["dates"]["date"]
        if isinstance(date_raw, list):
            (description,) = [e.get("#text") for e in date_raw if e.get("@dateType") == "Issued"]
        elif date_raw["@dateType"] == "Issued":
            date_string = date_raw["#text"]
            date_published = datetime.strptime(date_string, DATE_FORMAT)
        else:
            self._bad_record_format(id_, "date_published")
            return RecordError(
                id=id_, platform="zenodo", type="dataset", error="error decoding date_published"
            )

        if isinstance(record["publisher"], str):
            publisher = record["publisher"]
        else:
            self._bad_record_format(id_, "publisher")
            return RecordError(
                id=id_, platform="zenodo", type="dataset", error="error decoding publisher"
            )

        if isinstance(record["rightsList"]["rights"], list):
            license_ = record["rightsList"]["rights"][0]["@rightsURI"]
        elif isinstance(record["rightsList"]["rights"]["@rightsURI"], str):
            license_ = record["rightsList"]["rights"]["@rightsURI"]
        else:
            self._bad_record_format(id_, "license")
            return RecordError(
                id=id_, platform="zenodo", type="dataset", error="error decoding license"
            )

        keywords = []
        if "subjects" in record:
            if isinstance(record["subjects"]["subject"], str):
                keywords = [record["subjects"]["subject"]]
            elif isinstance(record["subjects"]["subject"], list):
                keywords = [item for item in record["subjects"]["subject"] if isinstance(item, str)]
            else:
                self._bad_record_format(id_, "keywords")
                return RecordError(
                    id=id_, platform="zenodo", type="dataset", error="error decoding keywords"
                )

        dataset = Dataset(
            platform="zenodo",
            platform_identifier=id_,
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

    def _get_resource_type(self, record):
        xml_string = record.raw
        start = xml_string.find('<resourceType resourceTypeGeneral="')
        if start != -1:
            start += len('<resourceType resourceTypeGeneral="')
            end = xml_string.find('"', start)
            if end != -1:
                return xml_string[start:end]
        id_, _ = self._get_record_dictionary(record)
        logging.error(f"Error while getting the resource type of the record {id_}")
        # Can return an RecordError Because we dont know the type
        return None

    def _retrieve_dataset_from_datetime(
        self, sk: Sickle, from_incl: datetime, to_excl: datetime | None = None
    ) -> Iterator[Dataset | RecordError]:
        records = sk.ListRecords(
            **{
                "metadataPrefix": "oai_datacite",
                "from": from_incl.isoformat(),
            }
        )

        record = next(records, None)
        last_date = None
        while record and (to_excl is None or (last_date is not None and last_date < to_excl)):
            if self._get_resource_type(record) == "Dataset":
                dataset = self._dataset_from_record(record)
                if not isinstance(dataset, RecordError):
                    last_date = dataset.date_published
                yield dataset
            record = next(records, None)

    def fetch(
        self, from_incl: datetime | None = None, to_excl: datetime | None = None
    ) -> Iterator[Dataset | RecordError]:
        sickle = Sickle("https://zenodo.org/oai2d")
        date = from_incl if from_incl is not None else datetime(2000, 1, 1, 12, 0, 0)
        return self._retrieve_dataset_from_datetime(sickle, date, to_excl=to_excl)
