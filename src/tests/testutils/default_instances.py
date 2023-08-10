"""
Fixtures that provide default instances for AIoD and ORM classes.

This way you have easy access to, for instance, an AIoDDataset filled with default values.
"""
import copy
import datetime
import json

import pytest

from database.model.dataset.dataset import Dataset
from database.model.dataset.alternate_name import DatasetAlternateName
from database.model.dataset.checksum import ChecksumORM
from database.model.dataset.checksum_algorithm import ChecksumAlgorithm
from database.model.dataset.data_download import DataDownloadORM
from database.model.dataset.measured_value import MeasuredValueORM
from database.model.general.keyword import KeywordOld
from database.model.general.license import LicenseOld
from tests.testutils.paths import path_test_resources


@pytest.fixture(scope="session")
def body_concept() -> dict:
    with open(path_test_resources() / "schemes" / "aiod" / "aiod_concept.json", "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def body_resource(body_concept: dict) -> dict:
    body = copy.copy(body_concept)
    with open(path_test_resources() / "schemes" / "aiod" / "ai_resource.json", "r") as f:
        resource = json.load(f)
    body.update(resource)
    return body


@pytest.fixture(scope="session")
def body_asset(body_resource: dict) -> dict:
    body = copy.copy(body_resource)
    with open(path_test_resources() / "schemes" / "aiod" / "ai_asset.json", "r") as f:
        asset = json.load(f)
    body.update(asset)
    return body


@pytest.fixture(scope="session")
def dataset() -> Dataset:
    return Dataset(
        identifier=7,
        description="description",
        name="name1",
        platform="platform",
        platform_identifier="1",
        same_as="sameAs",
        contact="contact",
        creator="creator",
        date_modified=datetime.datetime(2002, 1, 1),
        date_published=datetime.datetime(2001, 1, 1, 8),
        funder="funder",
        is_accessible_for_free=True,
        issn="12345678",
        size=100,
        spatial_coverage="spatial_coverage",
        temporal_coverage_from=datetime.datetime(2000, 1, 1),
        temporal_coverage_to=datetime.datetime(2000, 1, 2, 6),
        version="version1",
        license=LicenseOld(name="license.name"),
        has_parts=[],
        is_part=[],
        alternate_names=[
            DatasetAlternateName(name="alternative_1"),
            DatasetAlternateName(name="alternative_2"),
        ],
        citations=[],
        distributions=[
            DataDownloadORM(
                content_url="distr.content_url",
                content_size_kb=123,
                description="distr.description",
                name="distr.name",
                encoding_format="distr.encoding_format",
                checksum=[ChecksumORM(algorithm=ChecksumAlgorithm(name="md5"), value="md5hash")],
            )
        ],
        keywords=[KeywordOld(name="a"), KeywordOld(name="b"), KeywordOld(name="c")],
        measured_values=[MeasuredValueORM(variable="variable", technique="technique")],
    )
