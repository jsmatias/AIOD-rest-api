import datetime

# import math
import pytest
import time

import responses

from connectors.record_error import RecordError
from connectors.zenodo.zenodo_dataset_connector import ZenodoDatasetConnector
from database.model.agent.contact import Contact
from tests.testutils.paths import path_test_resources


with open(path_test_resources() / "connectors" / "zenodo" / "list_records_1.xml", "r") as f:
    records_list_1_expired_token = f.read()
    records_list_1 = records_list_1_expired_token.replace(
        'expirationDate="2024-02-08T17:40:07Z"', 'expirationDate="5000-02-08T17:40:07Z"'
    )

with open(path_test_resources() / "connectors" / "zenodo" / "list_records_2.xml", "r") as f:
    records_list_2 = f.read()


def test_fetch_happy_path():
    connector = ZenodoDatasetConnector()
    with responses.RequestsMock() as mocked_requests:
        mock_zenodo_responses_1(mocked_requests)

        from_incl = datetime.datetime(2023, 5, 23, 8, 0, 0)
        to_excl = datetime.datetime(2023, 5, 23, 9, 0, 0)
        resources = list(connector.run(state={}, from_incl=from_incl, to_excl=to_excl))
    datasets = [r for r in resources if not isinstance(r, RecordError)]
    errors = [r for r in resources if isinstance(r, RecordError)]
    assert {error.error for error in errors} == {"Wrong type"}
    assert len(datasets) == 6
    assert len(errors) == 45
    dataset = datasets[0].resource
    assert dataset.name == "kogalab21/all-alpha_design"
    expected = (
        "Source data and demos for the research article entitled “Design of "
        "complicated all-α protein structures” by Koya Sakuma, Naohiro Kobayashi, "
        "Toshihiko Sugiki, Toshio Nagashima, Toshimichi Fujiwara, Kano Suzuki, Naoya "
        "Kobayashi, Takeshi Murata, Takahiro Kosugi, Rie Koga, and Nobuyasu Koga."
    )
    assert dataset.description.plain.replace(" ", "").replace("\n", "") == expected.replace(" ", "")
    assert dataset.date_published == datetime.datetime(2023, 5, 18)
    assert dataset.license == "Other (Open)"
    assert dataset.platform == "zenodo"
    assert dataset.platform_resource_identifier == "zenodo.org:7947283"
    assert set(dataset.keyword) == set()

    creators: list[Contact] = datasets[0].related_resources["creator"]
    assert len(creators) == 1
    assert creators[0].name == "Nobuyasu Koga"

    (dataset_7902673,) = [
        d.resource
        for d in datasets
        if d.resource.platform_resource_identifier == "zenodo.org:7902673"
    ]
    distributions = dataset_7902673.distribution
    assert len(distributions) == 3
    distribution = distributions[0]
    assert distribution.name == "FIELDS_CONFIDE_CHECLIST.docx"
    assert distribution.encoding_format == "application/octet-stream"
    assert distribution.checksum == "97f511d24f8867405a8f87afbc76939d"
    assert distribution.checksum_algorithm == "md5"
    assert (
        distribution.content_url
        == "https://zenodo.org/api/records/7902673/files/FIELDS_CONFIDE_CHECLIST.docx/content"
    )


# def test_fetch_harvesting_rate_limit(mock_time_sleep):
#     connector = ZenodoDatasetConnector()
#     rate_limit_patch = 1
#     connector.harvesting_limit_per_minute = rate_limit_patch

#     with responses.RequestsMock() as mocked_requests:
#         mock_zenodo_responses_3(mocked_requests)
#         from_incl = datetime.datetime(2023, 5, 23, 8, 0, 0)
#         to_excl = datetime.datetime(2023, 5, 23, 9, 0, 0)
#         time_per_loop = datetime.timedelta(minutes=30)
#         resources = list(
#             connector.run(
#                 state={},
#                 from_incl=from_incl,
#                 to_excl=to_excl,
#                 time_per_loop=time_per_loop,
#             )
#         )

#         datasets = [r for r in resources if not isinstance(r, RecordError)]
#         errors = [r for r in resources if isinstance(r, RecordError)]
#         assert {error.error for error in errors} == {"Wrong type"}
#         assert len(datasets) == 12
#         assert len(errors) == 90
#         assert (
#             len(mock_time_sleep)
#             == math.ceil((to_excl - from_incl) / (time_per_loop * rate_limit_patch)) - 1
#         )


def test_fetch_expired_token_happy_path():
    connector = ZenodoDatasetConnector()
    with responses.RequestsMock() as mocked_requests:
        mock_zenodo_responses_2(mocked_requests)
        from_incl = datetime.datetime(2023, 5, 23, 8, 0, 0)
        to_excl = datetime.datetime(2023, 5, 23, 9, 0, 0)
        resources = list(connector.run(state={}, from_incl=from_incl, to_excl=to_excl))
        datasets = [r for r in resources if not isinstance(r, RecordError)]
        errors = [r for r in resources if isinstance(r, RecordError)]
        assert {error.error for error in errors} == {"Wrong type"}
        assert len(datasets) == 5
        assert len(errors) == 21


@pytest.fixture
def mock_time_sleep(monkeypatch):
    calls = []

    def mock_sleep(seconds):
        calls.append(seconds)

    monkeypatch.setattr(time, "sleep", mock_sleep)
    yield calls


def mock_zenodo_responses_1(mocked_requests: responses.RequestsMock):
    mock_first_list_response(
        mocked_requests,
        from_date="2023-05-23T08%3A00%3A00",
        until="2023-05-23T09%3A00%3A00",
        records_list=records_list_1,
    )
    mock_second_list_response(mocked_requests)
    mock_records_responses(mocked_requests)
    with open(path_test_resources() / "connectors" / "zenodo" / "7199024.json", "r") as f:
        body = f.read()
    mocked_requests.add(
        responses.GET, "https://zenodo.org/api/records/7199024/files", body=body, status=200
    )


def mock_zenodo_responses_2(mocked_requests: responses.RequestsMock):
    mock_first_list_response(
        mocked_requests,
        from_date="2023-05-23T08%3A00%3A00",
        until="2023-05-23T09%3A00%3A00",
        records_list=records_list_1_expired_token,
    )
    mock_records_responses(mocked_requests)


def mock_zenodo_responses_3(mocked_requests: responses.RequestsMock):

    mocked_requests.add(
        responses.GET,
        "https://zenodo.org/oai2d?"
        "metadataPrefix=oai_datacite&"
        "from=2023-05-23T08%3A00%3A00&"
        "until=2023-05-23T08%3A30%3A00&"
        "verb=ListRecords",
        body=records_list_1,
        status=200,
    )
    mocked_requests.add(
        responses.GET,
        "https://zenodo.org/oai2d?"
        "metadataPrefix=oai_datacite&"
        "from=2023-05-23T08%3A30%3A00&"
        "until=2023-05-23T09%3A00%3A00&"
        "verb=ListRecords",
        body=records_list_1,
        status=200,
    )
    mock_second_list_response(mocked_requests)
    mock_records_responses(mocked_requests)


def mock_first_list_response(mocked_requests, from_date: str, until: str, records_list: str):
    mocked_requests.add(
        responses.GET,
        "https://zenodo.org/oai2d?"
        "metadataPrefix=oai_datacite&"
        f"from={from_date}&"
        f"until={until}&"
        "verb=ListRecords",
        body=records_list,
        status=200,
    )


def mock_second_list_response(mocked_requests):
    mocked_requests.add(
        responses.GET,
        "https://zenodo.org/oai2d?"
        "resumptionToken=.resumption-token-to-page-2&"
        "verb=ListRecords",
        body=records_list_2,
        status=200,
    )


def mock_records_responses(mocked_requests):
    for id_ in (6884943, 7793917, 7947283, 7555467, 7902673):
        with open(path_test_resources() / "connectors" / "zenodo" / f"{id_}.json", "r") as f:
            body = f.read()
        mocked_requests.add(
            responses.GET, f"https://zenodo.org/api/records/{id_}/files", body=body, status=200
        )
