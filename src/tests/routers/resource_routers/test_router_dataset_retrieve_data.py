import copy
from unittest.mock import Mock

from http import HTTPStatus
from sqlalchemy.engine import Engine
from sqlmodel import Session
from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model.agent.person import Person


def test_get_data_from_default_with_no_distribution(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """Test getting data from a metadata with no distribution from default path.
    path: /datasets/v1/1/data/
    """

    keycloak_openid.userinfo = mocked_privileged_token

    with Session(engine) as session:
        session.add(person)
        session.commit()

    body = copy.deepcopy(body_asset)
    body["distribution"] = []

    testing_get_path = "/datasets/v1/1/data"
    expected_response_status_code = HTTPStatus.NOT_FOUND
    expected_err_msg = "Distribution not found!"

    # Add asset with no distributions
    response = client.post("/datasets/v1", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == HTTPStatus.OK, response.json()

    response = client.get(testing_get_path)

    assert response.status_code == expected_response_status_code, (
        f"The obtained status code {response.status_code} not same as expected: "
        f"{expected_response_status_code}"
    )

    response_json = response.json()
    assert (
        response_json["detail"] == expected_err_msg
    ), f"Error message not expected {response_json['detail']}"


def test_get_data_from_path_with_distribution_idx_with_no_distribution(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """Test getting data from a metadata with no distribution from path with distribution index.
    path: /datasets/v1/1/data/0
    """

    keycloak_openid.userinfo = mocked_privileged_token

    with Session(engine) as session:
        session.add(person)
        session.commit()

    body = copy.deepcopy(body_asset)
    body["distribution"] = []

    testing_get_path = "/datasets/v1/1/data/0"
    expected_response_status_code = HTTPStatus.NOT_FOUND
    expected_err_msg = "Distribution not found!"

    # Add asset with no distributions
    response = client.post("/datasets/v1", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == HTTPStatus.OK, response.json()

    response = client.get(testing_get_path)

    assert response.status_code == expected_response_status_code, (
        f"The obtained status code {response.status_code} not same as expected: "
        f"{expected_response_status_code}"
    )

    response_json = response.json()
    assert (
        response_json["detail"] == expected_err_msg
    ), f"Error message not expected {response_json['detail']}"


def test_get_data_from_default_path_with_one_distribution(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    """Test getting data from a metadata with no distribution from path with distribution index.
    path: /datasets/v1/1/data
    """

    keycloak_openid.userinfo = mocked_privileged_token

    with Session(engine) as session:
        session.add(person)
        session.commit()

    url_for_test = "https://zenodo.org/api/records/8206848/files/LPL11_July_2023.csv/content"
    filename = "LPL11_July_2023.csv"
    encoding_format = "text/csv"

    body = copy.deepcopy(body_asset)
    body["distribution"][0]["content_url"] = url_for_test
    body["distribution"][0]["name"] = filename
    body["distribution"][0]["encoding_format"] = encoding_format

    testing_get_path = "/datasets/v1/1/data"
    expected_response_status_code = HTTPStatus.OK
    expected_header_content_disposition = f"attachment; filename={filename}"
    expected_content_type = encoding_format
    expected_content_first_line = "time,battery,id,mag,mag_err,name,signal,tamb,tsky"

    # Add asset with no distributions
    response = client.post("/datasets/v1", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == HTTPStatus.OK, response.json()

    response = client.get(testing_get_path)

    assert response.status_code == expected_response_status_code, (
        f"The status code {response.status_code} didn't match with expected: "
        f"{expected_response_status_code}."
    )
    assert (
        response.headers.get("Content-Disposition") == expected_header_content_disposition
    ), "Content-Disposition o response doesn't match."

    assert (
        response.headers.get("Content-Type") == expected_content_type
    ), "Encoding format didn't match with expected"

    assert (
        str(response.content, encoding="utf-8").split("\n")[0] == expected_content_first_line
    ), "First line of the content of the response didn't match with expected"


# def test_get_data_from_default_path_with_one_distribution(
#     client: TestClient,
#     engine: Engine,
#     mocked_privileged_token: Mock,
#     body_asset: dict,
#     person: Person,
# ):
#     """Test getting data from a metadata with no distribution from path with distribution index.
#     path: /datasets/v1/1/data/0
#     """

#     keycloak_openid.userinfo = mocked_privileged_token

#     with Session(engine) as session:
#         session.add(person)
#         session.commit()

#     body = copy.deepcopy(body_asset)

#     testing_get_path = "/datasets/v1/1/data"
#     expected_response_status_code = HTTPStatus.OK
#     expected_err_msg = "Distribution not found!"

#     # Add asset with no distributions
#     response = client.post("/datasets/v1", json=body, headers={"Authorization": "Fake token"})
#     assert response.status_code == HTTPStatus.OK, response.json()

#     response = client.get(testing_get_path)

#     assert response.status_code == expected_response_status_code,
# f"The obtained status code {response.status_code} not same as expected:
# expected_response_status_code}"

#     response_json = response.json()
#     assert response_json["detail"] == expected_err_msg, f"Error
# message not expected {response_json['detail']}"

#     response0 = client.get("/datasets/v1/1/data/0")
#     assert response0.status_code == HTTPStatus.NOT_FOUND, response.json()

#     response0_json = response0.json()
#     assert response0_json["detail"] == "Distribution not found!"

#     response1 = client.get("/datasets/v1/1/data/1")
#     assert response1.status_code == HTTPStatus.NOT_FOUND, response.json()

#     response1_json = response1.json()
#     assert response1_json["detail"] == "Distribution not found!"
