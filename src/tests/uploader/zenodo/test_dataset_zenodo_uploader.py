import copy
import responses

import pytest
from unittest.mock import Mock

from fastapi import status
from sqlalchemy.engine import Engine
from sqlmodel import Session
from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model.agent.person import Person
from tests.testutils.paths import path_test_resources


#
# zenodo
# ACCESS_TOKEN = 'ChangeMe'
# r = requests.get('https://zenodo.org/api/deposit/depositions',
#                   params={'access_token': ACCESS_TOKEN})
# r.status_code
# # 200
# r.json()
# []
#
# bucket_url = r.json()["links"]["bucket"]

# ''' New API '''
# filename = "my-file.zip"
# path = "/path/to/%s" % filename

# '''
# The target URL is a combination of the bucket link with the desired filename
# seperated by a slash.
# '''
# with open(path, "rb") as fp:
#     r = requests.put(
#         "%s/%s" % (bucket_url, filename),
#         data=fp,
#         params=params,
#     )
# r.json()
# test 1 - Success uplooad

# Config
# ENDPOINT = f"upload/dataset/1/zenodo"
# ZENODO_BASE_URL = "https://zenodo.org/api/"
# ACCESS_TOKEN = "8HFii4bciYlV8jHaFgUDrXbn8FK8LSaNQGgh1H9nH2HR1k6NFLKNk7Xcsd8f"
# URL = "https://zenodo.org/api/deposit/depositions"

# ACCESS_TOKEN_TEST = "ldZeUa3zyXXNIvAWGyTFL3lL30PqYWZk2IaK4YTGsnV9cMX15j1Yv1R0doLa"
# URL_FOR_TEST = "https://sandbox.zenodo.org/api/deposit/depositions"
# headers = {"Content-Type": "application/json"}
# params = {"access_token": ACCESS_TOKEN_TEST}

# # 1. create an empty upload
# r = requests.post(URL_FOR_TEST, params=params, json={}, headers=headers)
# print(f"{r.status_code=}")
# print(f"{r.json()}")

# # 2. Upload metadata
# deposition_id = r.json()["id"]
# filename = "example1.csv"
# data = {
#     "metadata": {
#         "title": "My first upload",
#         "upload_type": "poster",
#         "description": "This is my first upload",
#         "creators": [{"name": "Doe, John", "affiliation": "Zenodo"}],
#     }
# }

# r = requests.put(
#     f"{URL_FOR_TEST}/{deposition_id}", params=params, data=json.dumps(data), headers=headers
# )
# r.status_code

# # 3. Upload metadata to AIoD
# # Convert metadata to AIoD format
# # Get AIoD id for this metadata
# aiod_identifier = 1
# endpoint = f"upload/datasets/{aiod_identifier}/zenodo"

# #####################################################################
# #  Assuming this metadata is already created and synced with zenodo
# ####

# # 4. upload a new file
# # a. Get the platform id
# platform_resource_id = get_dataset(aiod_identifier)["platform_resource_identifier"]
# # Get bucket_url
# r = requests.get(f"{URL_FOR_TEST}/{platform_resource_id}", params=params)
# bucket_url = r.json()["links"]["bucket"]

# with open(path_test_resources() / "contents" / filename, "rb") as f:
#     r = requests.put(f"{bucket_url}/{filename}", data=f, params=params)
# print(r.json())

# # 3. get the new updated file
# r = requests.get(URL_FOR_TEST, params={"access_token": ACCESS_TOKEN})
# print(f"{r.status_code=}")
# print(r.json())


URL_FOR_TEST = "https://sandbox.zenodo.org/api/deposit/depositions"


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


def mock_response(mocked_requests: responses.RequestsMock):
    mocked_requests.add(
        responses.POST,
        URL_FOR_TEST,
        status=200,
    )


@pytest.mark.skip(reason="Not implemented yet.")
def test_happy_path_upload(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    body = copy.deepcopy(body_asset)
    set_up(client, engine, mocked_privileged_token, body, person)

    ACCESS_TOKEN_TEST = "ldZeUa3zyXXNIvAWGyTFL3lL30PqYWZk2IaK4YTGsnV9cMX15j1Yv1R0doLa"
    headers = {"Content-Type": "text/csv"}
    params = {"access_token": ACCESS_TOKEN_TEST}

    aiod_identifier = 1
    endpoint = f"upload/datasets/{aiod_identifier}/zenodo"

    with responses.RequestsMock() as mocked_requests:
        mock_response(mocked_requests)

        with open(path_test_resources() / "contents" / "example1.csv", "rb") as f:
            files = {"file": f}
            response = client.post(endpoint, params=params, headers=headers, files=files)

        assert response.status_code == status.HTTP_200_OK, response.json()
