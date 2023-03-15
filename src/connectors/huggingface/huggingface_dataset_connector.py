import logging
import typing

import bibtexparser as bibtexparser
import datasets
import dateutil.parser
import requests

from connectors import DatasetConnector
from database.models import DatasetDescription, DataDownload, Keyword, Publication, License


class HuggingFaceDatasetConnector(DatasetConnector):
    def fetch(self, node_specific_identifier: str) -> DatasetDescription:
        raise NotImplementedError()

    @staticmethod
    def _get(url: str, dataset_id: str) -> typing.List[typing.Dict[str, typing.Any]]:
        """
        Perform a GET request and raise an exception if the response code is not OK.
        """
        response = requests.get(url, params={"dataset": dataset_id})
        response_json = response.json()
        if not response.ok:
            msg = response_json["error"]
            logging.error(
                f"Error while fetching parquet info for dataset {dataset_id}: " f"'{msg}'"
            )
            return []
        return response_json["parquet_files"]

    def fetch_all(self, limit: int | None = None) -> typing.Iterator[DatasetDescription]:
        ds = datasets.list_datasets(with_details=True)[:limit]
        for dataset in ds:
            citations = []
            if dataset.citation is not None:
                parsed_citations = bibtexparser.loads(dataset.citation).entries
                if len(parsed_citations) == 0:
                    citations = [Publication(title=dataset.citation)]
                elif len(parsed_citations) == 1:
                    citation = parsed_citations[0]
                    citations = [
                        Publication(
                            title=citation["title"],
                            url=citation["link"] if "link" in citation else None,
                        )
                    ]
                else:
                    raise ValueError(
                        f"Unexpected number of citations found for dataset "
                        f"{dataset.id} in {dataset.citation}: {len(parsed_citations)}"
                    )

            parquet_info = HuggingFaceDatasetConnector._get(
                url="https://datasets-server.huggingface.co/parquet", dataset_id=dataset.id
            )
            distributions = [
                DataDownload(
                    name=pq_file["filename"],
                    description=f"{pq_file['dataset']}. Config: {pq_file['config']}. Split: "
                    f"{pq_file['split']}",
                    content_url=pq_file["url"],
                    content_size_kb=pq_file["size"],
                )
                for pq_file in parquet_info
            ]
            size = None
            ds_license = None
            if dataset.cardData is not None:
                if isinstance(dataset.cardData["license"], str):
                    ds_license = dataset.cardData["license"]
                else:
                    (ds_license,) = dataset.cardData["license"]

                if "dataset_info" in dataset.cardData:
                    size = sum(
                        split["num_examples"]
                        for split in dataset.cardData["dataset_info"]["splits"]
                    )
            yield DatasetDescription(
                description=dataset.description,
                name=dataset.id,
                node_specific_identifier=dataset.id,
                node=self.node_name,
                same_as=f"https://huggingface.co/datasets/{dataset.id}",
                creator=dataset.author,
                date_modified=dateutil.parser.parse(dataset.lastModified),
                citations=citations,
                license=License(name=ds_license) if ds_license is not None else None,
                distributions=distributions,
                is_accessible_for_free=True,
                size=size,
                keywords=[Keyword(name=tag) for tag in dataset.tags],
            )
