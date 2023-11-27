import copy
import responses

from unittest.mock import Mock, patch


from fastapi import status
from sqlalchemy.engine import Engine
from sqlmodel import Session
from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model.agent.person import Person
from tests.testutils.paths import path_test_resources

from tests.uploader.zenodo.mock_zenodo import MockZenodoResponse
from uploader.zenodo_uploader import ZenodoUploader

ENDPOINT = "/upload/datasets/1/zenodo"
FILE1 = "example1.csv"
FILE2 = "example2.tsv"

ZENODO_BASE_URL = "https://zenodo.org/api/deposit/depositions"
ZENODO_REPO_URL = "https://zenodo.org/api/files/fake-bucket-id00"
ZENODO_REPO_ID = 100

mocked_zenodo_responses = MockZenodoResponse(ZENODO_REPO_ID, ZENODO_BASE_URL, ZENODO_REPO_URL)


def distribution_from_metadata(filename: str) -> dict:
    file_metadata = mocked_zenodo_responses.generate_file_metadata(filename)
    dist = {
        "platform": "zenodo",
        "platform_resource_identifier": file_metadata["id"],
        "checksum": file_metadata["checksum"],
        "content_url": file_metadata["links"]["download"],
        "content_size_kb": file_metadata["filesize"],
        "name": file_metadata["filename"],
    }
    return dist


def mock_response_generator(
    mocked_requests: responses.RequestsMock, existing_files: list[str], new_file: list[str]
):
    """
    Generates mocked responses for zenodo with or without files already uploaded to the repo.
    """
    mocked_requests.add(
        responses.GET,
        f"{ZENODO_BASE_URL}/{ZENODO_REPO_ID}",
        json=mocked_zenodo_responses.get_metadata(new_file),
        status=200,
    )
    mocked_requests.add(
        responses.POST,
        ZENODO_BASE_URL,
        json=mocked_zenodo_responses.create_repo(metadata={}),
        status=201,
    )
    mocked_requests.add(
        responses.PUT,
        f"{ZENODO_BASE_URL}/{ZENODO_REPO_ID}",
        json=mocked_zenodo_responses.add_metadata(existing_files),
        status=200,
    )
    mocked_requests.add(
        responses.PUT,
        f"{ZENODO_REPO_URL}/example1.csv",
        json=mocked_zenodo_responses.add_file(),
        status=201,
    )


def set_up(
    client: TestClient, engine: Engine, mocked_privileged_token: Mock, body: dict, person: Person
):
    """
    Set up the test environment for API endpoint testing.
    This function prepares the test environment by mocking user info,
    adding a person to the database, and sending a POST request to the
    specified endpoint for the given resource.
    """
    keycloak_openid.userinfo = mocked_privileged_token
    with Session(engine) as session:
        session.add(person)
        session.commit()

    response = client.post("/datasets/v1", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == status.HTTP_200_OK, response.json()


def test_happy_path_creating_repo(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """
    Test the successful path for creating a new repository on Zenodo before uploading a file.
    The creating of a new repo is triggered when platform_resource_identifier is None.
    """

    body = copy.deepcopy(body_asset)
    body["platform"] = None
    body["platform_resource_identifier"] = None
    body["distribution"] = []

    set_up(client, engine, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token"}

    with responses.RequestsMock() as mocked_requests:
        mock_response_generator(mocked_requests, existing_files=[], new_file=[FILE1])

        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == 1, response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "zenodo", response_json
    assert (
        response_json["platform_resource_identifier"] == f"zenodo.org:{ZENODO_REPO_ID}"
    ), response_json

    assert len(response_json["distribution"]) == 1
    assert response_json["distribution"] == [distribution_from_metadata(FILE1)], response_json


def test_happy_path_existing_repo(
    client: TestClient,
    engine: Engine,
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
    body["platform_resource_identifier"] = f"zenodo.org:{ZENODO_REPO_ID}"
    body["distribution"] = []

    set_up(client, engine, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token"}

    with responses.RequestsMock(assert_all_requests_are_fired=False) as mocked_requests:
        mock_response_generator(mocked_requests, existing_files=[], new_file=[FILE1])

        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            with patch.object(
                ZenodoUploader,
                "_get_metadata_from_zenodo",
                side_effect=[
                    mocked_zenodo_responses.get_metadata(),
                    mocked_zenodo_responses.get_metadata([FILE1]),
                ],
            ):
                response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == 1, response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "zenodo", response_json
    assert (
        response_json["platform_resource_identifier"] == f"zenodo.org:{ZENODO_REPO_ID}"
    ), response_json

    assert len(response_json["distribution"]) == 1
    assert response_json["distribution"] == [distribution_from_metadata(FILE1)], response_json


def test_happy_path_existing_file(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """
    Test uploading a second file to zenodo.
    """

    body = copy.deepcopy(body_asset)
    body["platform"] = "zenodo"
    body["platform_resource_identifier"] = f"zenodo.org:{ZENODO_REPO_ID}"
    body["distribution"] = [distribution_from_metadata(FILE1)]

    set_up(client, engine, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token"}

    with responses.RequestsMock(assert_all_requests_are_fired=False) as mocked_requests:
        mock_response_generator(mocked_requests, existing_files=[FILE1], new_file=[FILE2])

        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            with patch.object(
                ZenodoUploader,
                "_get_metadata_from_zenodo",
                side_effect=[
                    mocked_zenodo_responses.get_metadata([FILE1]),
                    mocked_zenodo_responses.get_metadata([FILE1, FILE2]),
                ],
            ):
                response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == 1, response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "zenodo", response_json
    assert (
        response_json["platform_resource_identifier"] == f"zenodo.org:{ZENODO_REPO_ID}"
    ), response_json

    assert len(response_json["distribution"]) == 2
    assert response_json["distribution"] == body["distribution"] + [
        distribution_from_metadata(FILE2)
    ], response_json


def test_happy_path_updating_an_existing_file(
    client: TestClient,
    engine: Engine,
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
    body["platform_resource_identifier"] = f"zenodo.org:{ZENODO_REPO_ID}"
    body["distribution"] = [distribution_from_metadata(FILE1)]

    set_up(client, engine, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token"}

    get_res1 = mocked_zenodo_responses.get_metadata([FILE1])
    get_res2 = copy.deepcopy(get_res1)
    get_res2["files"][0]["id"] += "new"

    with responses.RequestsMock(assert_all_requests_are_fired=False) as mocked_requests:
        mock_response_generator(mocked_requests, existing_files=[FILE1], new_file=[FILE1])

        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            with patch.object(
                ZenodoUploader,
                "_get_metadata_from_zenodo",
                side_effect=[
                    get_res1,
                    get_res2,
                ],
            ):
                response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == 1, response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "zenodo", response_json
    assert (
        response_json["platform_resource_identifier"] == f"zenodo.org:{ZENODO_REPO_ID}"
    ), response_json

    assert len(response_json["distribution"]) == 1
    expected_updated_dist = distribution_from_metadata(FILE1)
    expected_updated_dist["platform_resource_identifier"] = get_res2["files"][0]["id"]
    assert response_json["distribution"] == [expected_updated_dist], response_json


def test_platform_name_conflict(
    client: TestClient,
    engine: Engine,
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
    body["platform_resource_identifier"] = f"zenodo.org:{ZENODO_REPO_ID}"
    body["distribution"] = []

    set_up(client, engine, mocked_privileged_token, body, person)

    headers = {"Authorization": "Fake token"}
    params = {"token": "fake-token"}

    with responses.RequestsMock(assert_all_requests_are_fired=False) as mocked_requests:
        mock_response_generator(mocked_requests, existing_files=[], new_file=[FILE1])

        with open(path_test_resources() / "contents" / FILE1, "rb") as f:
            test_file = {"file": f}
            with patch.object(
                ZenodoUploader,
                "_get_metadata_from_zenodo",
                side_effect=[
                    mocked_zenodo_responses.get_metadata(),
                    mocked_zenodo_responses.get_metadata([FILE1]),
                ],
            ):
                response = client.post(ENDPOINT, params=params, headers=headers, files=test_file)

        assert response.status_code == status.HTTP_409_CONFLICT, response.json()
        assert response.json()["detail"] == (
            "Platform name huggingface conflict! "
            "Verify that the platform name in the metadata is either 'zenodo' or empty"
        ), response.json()

    response_json = client.get("datasets/v1/1").json()

    assert response_json["platform"] == "huggingface", response_json
    assert (
        response_json["platform_resource_identifier"] == f"zenodo.org:{ZENODO_REPO_ID}"
    ), response_json

    assert len(response_json["distribution"]) == 0
