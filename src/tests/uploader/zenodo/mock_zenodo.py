"""
    Generates mocked responses for zenodo endpoints.
    - POST to BASE_URL: Creates an empty record
    - GET to BASE_URL/RESOURCE_ID: Gets the info of the record.
    - PUT to BASE_URL/REOURCE_ID: Updates metadata
    - PUT to REPO_URL/FILE_NAME: Uploads a file
    - POST to BASE_URL/REOURCE_ID/actions/publish: Publishes the dataset with all content
    - GET to BASE_URL/RESOURCE_ID/files: Gets the list of files in draft mode
    - GET to RECORDS_URL/RESOURCE_ID/files: Gets the list of published data
"""

import responses

BASE_URL = "https://zenodo.org/api/deposit/depositions"
REPO_URL = "https://zenodo.org/api/files/fake-bucket-id00"
RECORDS_URL = "https://zenodo.org/api/records"
RESOURCE_ID = 100


def mock_create_repo(mocked_requests: responses.RequestsMock) -> responses.RequestsMock:
    mocked_requests.add(
        responses.POST,
        BASE_URL,
        json=record_response(),
        status=201,
    )

    return mocked_requests


def mock_get_repo_metadata(
    mocked_requests: responses.RequestsMock, is_published: bool = False
) -> responses.RequestsMock:
    mocked_requests.add(
        responses.GET,
        f"{BASE_URL}/{RESOURCE_ID}",
        json=record_response(is_published),
        status=200,
    )

    return mocked_requests


def mock_update_metadata(mocked_requests: responses.RequestsMock) -> responses.RequestsMock:
    mocked_requests.add(
        responses.PUT,
        f"{BASE_URL}/{RESOURCE_ID}",
        json={},
        status=200,
    )
    return mocked_requests


def mock_upload_file(
    mocked_requests: responses.RequestsMock, new_file: str
) -> responses.RequestsMock:
    mocked_requests.add(
        responses.PUT,
        f"{REPO_URL}/{new_file}",
        json={},
        status=201,
    )
    return mocked_requests


def mock_publish_resource(mocked_requests: responses.RequestsMock) -> responses.RequestsMock:
    mocked_requests.add(
        responses.POST,
        f"{BASE_URL}/{RESOURCE_ID}/actions/publish",
        json=publish_response(),
        status=202,
    )
    return mocked_requests


def mock_get_draft_files(
    mocked_requests: responses.RequestsMock, files: list[str]
) -> responses.RequestsMock:
    mocked_requests.add(
        responses.GET,
        f"{BASE_URL}/{RESOURCE_ID}/files",
        json=draft_files_response(files),
        status=200,
    )
    return mocked_requests


def mock_get_published_files(
    mocked_requests: responses.RequestsMock, files: list[str]
) -> responses.RequestsMock:
    mocked_requests.add(
        responses.GET,
        f"{RECORDS_URL}/{RESOURCE_ID}/files",
        json=published_files_reponse(files),
        status=200,
    )
    return mocked_requests


def record_response(is_published: bool = False) -> dict:
    response = {
        "id": RESOURCE_ID,
        # just the state `done` matters here
        "state": "done" if is_published else "unsubmitted/inprogress",
        "links": {"bucket": REPO_URL, "record": f"{RECORDS_URL}/{RESOURCE_ID}"},
    }
    return response


def publish_response() -> dict:
    response = {"links": {"record": f"{RECORDS_URL}/{RESOURCE_ID}"}}
    return response


def draft_files_response(filenames: list[str]) -> list[dict]:
    """Truncated reponse from zenodo when a request is made to the draft repo url."""
    response = [
        {"id": f"123-{name}", "filename": name, "filesize": 20, "checksum": "12345abcd"}
        for name in filenames
    ]
    return response


def published_files_reponse(filenames: list[str]) -> dict[str, list[dict]]:
    """Truncated reponse from zenodo when a request is made to the public repo url."""
    response = {
        "entries": [
            {
                "key": name,
                "file_id": f"123-{name}",
                "checksum": "12345abcd",
                "size": 20,
                "links": {"content": f"{RECORDS_URL}/{RESOURCE_ID}/files/{name}/content"},
            }
            for name in filenames
        ]
    }

    return response
