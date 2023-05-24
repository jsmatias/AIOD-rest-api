from datetime import datetime
from typing import Iterator
from sickle import Sickle
import xmltodict

from connectors import ResourceConnector
from platform_names import PlatformName
from schemas import AIoDDataset


class ZenodoDatasetConnector(ResourceConnector[AIoDDataset]):
    @property
    def platform_name(self) -> PlatformName:
        return PlatformName.zenodo

    def fetch(self, platform_identifier: str) -> AIoDDataset:
        raise Exception("Not implemented")

    def _get_record_dictionary(self, record):
        xml_string = record.raw
        xml_dict = xmltodict.parse(xml_string)
        return xml_dict["record"]["metadata"]["oai_datacite"]["payload"]["resource"]

    def _dataset_from_record(self, record) -> AIoDDataset:
        creator = ""
        if isinstance(record["creators"]["creator"], list):
            creators_list = [item["creatorName"] for item in record["creators"]["creator"]]
            creator = ", ".join(creators_list)  # TODO change field to an array
        elif isinstance(record["creators"]["creator"]["creatorName"], str):
            creator = record["creators"]["creator"]["creatorName"]

        title = ""
        if isinstance(record["titles"]["title"], str):
            title = record["titles"]["title"]

        description = ""
        if isinstance(record["descriptions"]["description"], list):
            for element in record["descriptions"]["description"]:
                if element.get("@descriptionType") == "Abstract":
                    description = element.get("#text")
                    break
        elif record["descriptions"]["description"]["@descriptionType"] == "Abstract":
            description = record["descriptions"]["description"]["#text"]

        date_published = None
        date_format = "%Y-%m-%d"
        if isinstance(record["dates"]["date"], list):
            for element in record["dates"]["date"]:
                if element.get("@dateType") == "Issued":
                    date_string = element["#text"]
                    date_published = datetime.strptime(date_string, date_format)
                    break
        elif record["dates"]["date"]["@dateType"] == "Issued":
            date_string = record["dates"]["date"]["#text"]
            date_published = datetime.strptime(date_string, date_format)

        publisher = ""
        if isinstance(record["publisher"], str):
            publisher = record["publisher"]

        # Get dataset keywords
        keywords = []

        if "subjects" in record:
            if isinstance(record["subjects"]["subject"], str):
                keywords = [record["subjects"]["subject"]]
            elif isinstance(record["subjects"]["subject"], list):
                keywords = [item for item in record["subjects"]["subject"] if isinstance(item, str)]

        dataset = AIoDDataset(
            name=title[:150],
            same_as="",
            creator=creator[
                :150
            ],  # TODO not enough characters for creator list, change to array or allow more length
            description=description[:500],
            date_published=date_published,
            publisher=publisher,
            keywords=keywords,
        )
        return dataset

    def _retrieve_dataset_from_datetime(self, sk: Sickle, dt: datetime):
        records = sk.ListRecords(
            **{
                "metadataPrefix": "oai_datacite",
                "from": dt.isoformat(),
            }
        )
        for record in records:
            record_dict = self._get_record_dictionary(record)

            if record_dict["resourceType"]["@resourceTypeGeneral"] == "Dataset":
                yield self._dataset_from_record(record_dict)

    def fetch_all(self, limit: int | None = None) -> Iterator[AIoDDataset]:
        sickle = Sickle("https://zenodo.org/oai2d")
        date = datetime(2000, 5, 23, 12, 0, 0)  # this should be a paramater
        return self._retrieve_dataset_from_datetime(sickle, date)
