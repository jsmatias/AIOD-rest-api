import copy
import responses

from unittest.mock import Mock

from fastapi import status
from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model.agent.person import Person
from database.model.platform.platform_names import PlatformName
from database.session import DbSession

from tests.testutils.paths import path_test_resources

import tests.uploader.zenodo.mock_zenodo as zenodo

ENDPOINT = "/upload/datasets/1/zenodo"
FILE1 = "example1.csv"
FILE2 = "example2.tsv"


def distribution_from_zenodo(*filenames: str, is_published: bool = False) -> list[dict]:
    files_metadata = (
        zenodo.files_response_from_published(*filenames)["entries"]
        if is_published
        else zenodo.files_response_from_draft(*filenames)
    )
    dist = [
        {
            "platform": "zenodo",
            "platform_resource_identifier": file["file_id" if is_published else "id"],
            "checksum": file["checksum"].split(":")[-1] if is_published else file["checksum"],
            "checksum_algorithm": file["checksum"].split(":")[0] if is_published else "md5",
            "content_url": file["links"]["content" if is_published else "download"],
            "content_size_kb": round(file["size" if is_published else "filesize"] / 1000),
            "name": file["key" if is_published else "filename"],
        }
        for file in files_metadata
    ]
    return dist


def set_up(client: TestClient, mocked_privileged_token: Mock, body: dict, person: Person):
    """
    Set up the test environment for API endpoint testing.
    This function prepares the test environment by mocking user info,
    adding a person to the database, and sending a POST request to the
    specified endpoint for the given resource.
    """
    keycloak_openid.introspect = mocked_privileged_token

    with DbSession() as session:
        session.add(person)
        session.commit()

    response = client.post("/datasets/v1", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == status.HTTP_200_OK, response.json()


def test_happy_path_creating_repo(
    client: TestClient,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """
    Test the successful path for creating a new repository on Zenodo before uploading a file.
    The creation of a new repo must be triggered when platform_resource_identifier is None.
    """

    body = copy.deepcopy(body_asset)
    body["platform"] = None
    body["platform_resource_identifier"] = None
    body["distribution"] = []

    set_up(client, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token", "publish": False}

    with responses.RequestsMock() as mocked_requests:
        mocked_requests = zenodo.mock_create_repo(mocked_requests)
        mocked_requests = zenodo.mock_upload_file(mocked_requests, FILE1)
        zenodo.mock_get_draft_files(mocked_requests, [FILE1])

        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == 1, response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "zenodo", response_json
    assert (
        response_json["platform_resource_identifier"] == f"zenodo.org:{zenodo.RESOURCE_ID}"
    ), response_json

    assert response_json["distribution"] == distribution_from_zenodo(FILE1), response_json


def test_happy_path_existing_repo(
    client: TestClient,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """
    Test the successful path for an existing repository on Zenodo.
    When the platform_resource_identifier is not None (zenodo.org:int) the code should
    get metadata and url of the existing repo, then upload a file.
    """

    body = copy.deepcopy(body_asset)
    body["platform"] = "zenodo"
    body["platform_resource_identifier"] = f"zenodo.org:{zenodo.RESOURCE_ID}"
    body["distribution"] = []

    set_up(client, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token"}

    with responses.RequestsMock() as mocked_requests:
        mocked_requests = zenodo.mock_get_repo_metadata(mocked_requests)
        mocked_requests = zenodo.mock_update_metadata(mocked_requests)
        mocked_requests = zenodo.mock_upload_file(mocked_requests, FILE1)
        zenodo.mock_get_draft_files(mocked_requests, [FILE1])

        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == 1, response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "zenodo", response_json
    assert (
        response_json["platform_resource_identifier"] == f"zenodo.org:{zenodo.RESOURCE_ID}"
    ), response_json

    assert response_json["distribution"] == distribution_from_zenodo(FILE1), response_json


def test_happy_path_existing_file(
    client: TestClient,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """
    Test uploading a second file to zenodo.
    """

    body = copy.deepcopy(body_asset)
    body["platform"] = "zenodo"
    body["platform_resource_identifier"] = f"zenodo.org:{zenodo.RESOURCE_ID}"
    body["distribution"] = distribution_from_zenodo(FILE1)

    set_up(client, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token"}

    with responses.RequestsMock(assert_all_requests_are_fired=False) as mocked_requests:
        mocked_requests = zenodo.mock_get_repo_metadata(mocked_requests)
        mocked_requests = zenodo.mock_update_metadata(mocked_requests)
        mocked_requests = zenodo.mock_upload_file(mocked_requests, FILE2)
        zenodo.mock_get_draft_files(mocked_requests, [FILE1, FILE2])

        with open(path_test_resources() / "contents" / FILE2, "rb") as f:
            test_file = {"file": f}
            response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == 1, response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "zenodo", response_json
    assert (
        response_json["platform_resource_identifier"] == f"zenodo.org:{zenodo.RESOURCE_ID}"
    ), response_json

    assert response_json["distribution"] == body["distribution"] + distribution_from_zenodo(
        FILE2
    ), response_json


def test_happy_path_updating_an_existing_file(
    client: TestClient,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """
    Test uploading a second file to zenodo with the same name.
    This must update the existing file.
    """

    body = copy.deepcopy(body_asset)
    body["platform"] = "zenodo"
    body["platform_resource_identifier"] = f"zenodo.org:{zenodo.RESOURCE_ID}"
    body["distribution"] = distribution_from_zenodo(FILE1)

    set_up(client, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token"}

    updated_file_new_id = "new-fake-id"

    with responses.RequestsMock() as mocked_requests:
        mocked_requests = zenodo.mock_get_repo_metadata(mocked_requests)
        mocked_requests = zenodo.mock_update_metadata(mocked_requests)
        mocked_requests = zenodo.mock_upload_file(mocked_requests, FILE1)

        draft_response = zenodo.files_response_from_draft(FILE1)
        draft_response[0]["id"] = updated_file_new_id
        mocked_requests.add(
            responses.GET,
            f"{zenodo.BASE_URL}/{zenodo.RESOURCE_ID}/files",
            json=draft_response,
            status=200,
        )

        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == 1, response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "zenodo", response_json
    assert (
        response_json["platform_resource_identifier"] == f"zenodo.org:{zenodo.RESOURCE_ID}"
    ), response_json

    expected_updated_dist = distribution_from_zenodo(FILE1)
    expected_updated_dist[0]["platform_resource_identifier"] = updated_file_new_id
    assert response_json["distribution"] == expected_updated_dist, response_json


def test_happy_path_publishing(
    client: TestClient,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """
    Test publishing the resource on Zenodo after uploading a file.
    The URL of the content should not be empty
    """

    body = copy.deepcopy(body_asset)
    body["platform"] = None
    body["platform_resource_identifier"] = None
    body["distribution"] = []

    set_up(client, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token", "publish": True}

    with responses.RequestsMock() as mocked_requests:
        mocked_requests = zenodo.mock_create_repo(mocked_requests)
        mocked_requests = zenodo.mock_upload_file(mocked_requests, FILE1)
        mocked_requests = zenodo.mock_publish_resource(mocked_requests)
        zenodo.mock_get_published_files(mocked_requests, [FILE1])

        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == 1, response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "zenodo", response_json
    assert (
        response_json["platform_resource_identifier"] == f"zenodo.org:{zenodo.RESOURCE_ID}"
    ), response_json

    assert response_json["distribution"] == distribution_from_zenodo(
        FILE1, is_published=True
    ), response_json


def test_attempt_to_upload_published_resource(
    client: TestClient,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """
    Test attempt to upload a file to a resource that has already been published.
    This must raise an error 423 (locked) and return a message stating
    that the process can't be concluded.
    """

    body = copy.deepcopy(body_asset)
    body["platform"] = "zenodo"
    body["platform_resource_identifier"] = f"zenodo.org:{zenodo.RESOURCE_ID}"
    body["distribution"] = distribution_from_zenodo(FILE1, is_published=True)

    set_up(client, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token", "publish": True}

    with responses.RequestsMock() as mocked_requests:
        zenodo.mock_get_repo_metadata(mocked_requests, is_published=True)

        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_409_CONFLICT, response.json()
        assert response.json()["detail"] == [
            "This resource is already public and "
            "can't be edited with this endpoint. "
            "You can access and modify it at "
            f"{zenodo.RECORDS_URL}/{zenodo.RESOURCE_ID}"
        ], response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["distribution"] == body["distribution"], response_json


def test_platform_name_conflict(
    client: TestClient,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """
    Test error handling on the attempt to upload a dataset with a platform name
    different than zenodo.
    """

    body = copy.deepcopy(body_asset)
    body["platform"] = "huggingface"
    body["platform_resource_identifier"] = "fake-id"
    body["distribution"] = []

    set_up(client, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token"}

    with responses.RequestsMock():
        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert response.json()["detail"] == (
            "The dataset with identifier 1 should have platform=" f"{PlatformName.zenodo}."
        ), response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "huggingface", response_json
    assert response_json["platform_resource_identifier"] == "fake-id", response_json

    assert response_json["distribution"] == []
