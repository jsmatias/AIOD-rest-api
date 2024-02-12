import responses

from tests.testutils.paths import path_test_resources


TOKEN_EXPIRATION_DATETIME = "2024-02-08T17:40:07Z"

with open(path_test_resources() / "connectors" / "zenodo" / "list_records_1.xml", "r") as f:
    records_list_1 = f.read()

with open(path_test_resources() / "connectors" / "zenodo" / "list_records_2.xml", "r") as f:
    records_list_2 = f.read()


def first_list_response(mocked_requests: responses.RequestsMock):
    mocked_requests.add(
        responses.GET,
        "https://zenodo.org/oai2d?"
        "metadataPrefix=oai_datacite&"
        "from=2023-05-23T08%3A00%3A00&"
        "until=2023-05-23T09%3A00%3A00&"
        "verb=ListRecords",
        body=records_list_1,
        status=200,
    )


def second_list_response(mocked_requests: responses.RequestsMock):
    mocked_requests.add(
        responses.GET,
        "https://zenodo.org/oai2d?"
        "resumptionToken=.resumption-token-to-page-2&"
        "verb=ListRecords",
        body=records_list_2,
        status=200,
    )


def record_response(mocked_requests: responses.RequestsMock, id_: int):
    with open(path_test_resources() / "connectors" / "zenodo" / f"{id_}.json", "r") as f:
        body = f.read()
    mocked_requests.add(
        responses.GET, f"https://zenodo.org/api/records/{id_}/files", body=body, status=200
    )


def first_list_records_responses(mocked_requests: responses.RequestsMock):
    for id_ in (6884943, 7793917, 7947283, 7555467, 7902673):
        record_response(mocked_requests, id_)


def second_list_records_responses(mocked_requests: responses.RequestsMock):
    record_response(mocked_requests, 7199024)
