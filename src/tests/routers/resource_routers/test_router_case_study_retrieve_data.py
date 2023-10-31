import copy
import time
from unittest.mock import Mock

from fastapi import status
from sqlalchemy.engine import Engine
from sqlmodel import Session
from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model.agent.person import Person

resource_name = "case_studies"
default_path = f"{resource_name}/v1/1/data"


def test_get_data_from_default_with_no_distribution(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    f"""Test getting the actual data from a metadata with no distribution.
    Test for the default path (without distribution index): /{resource_name}/v1/1/data/
    """

    keycloak_openid.userinfo = mocked_privileged_token

    with Session(engine) as session:
        session.add(person)
        session.commit()

    body = copy.deepcopy(body_asset)
    body["distribution"] = []

    testing_get_path = default_path
    expected_response_status_code = status.HTTP_404_NOT_FOUND
    expected_err_msg = "Distribution not found."

    # Add asset with no distributions
    response = client.post(
        f"/{resource_name}/v1", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

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
    f"""Test getting the actual data from a metadata with no distribution.
    Test for the path with distribution index: /{resource_name}/v1/1/data/0/
    """

    keycloak_openid.userinfo = mocked_privileged_token

    with Session(engine) as session:
        session.add(person)
        session.commit()

    body = copy.deepcopy(body_asset)
    body["distribution"] = []

    testing_get_path = default_path + "/0"
    expected_response_status_code = status.HTTP_404_NOT_FOUND
    expected_err_msg = "Distribution not found."

    # Add asset with no distributions
    response = client.post(
        f"/{resource_name}/v1", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

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
    f"""Test getting the actual data from a metadata with one distribution.
    Test for the default path (without distribution index): /{resource_name}/v1/1/data/
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

    testing_get_path = default_path
    expected_response_status_code = status.HTTP_200_OK
    expected_header_content_disposition = f"attachment; filename={filename}"
    expected_content_type = encoding_format
    expected_content_first_line = "time,battery,id,mag,mag_err,name,signal,tamb,tsky"

    # Add asset with no distributions
    response = client.post(
        f"/{resource_name}/v1", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response = client.get(testing_get_path)

    assert response.status_code == expected_response_status_code, (
        f"The status code {response.status_code} didn't match with expected: "
        f"{expected_response_status_code}."
    )
    assert (
        response.headers.get("Content-Disposition") == expected_header_content_disposition
    ), "Content-Disposition of response doesn't match."

    assert (
        response.headers.get("Content-Type") == expected_content_type
    ), "Encoding format didn't match with expected"

    assert (
        str(response.content, encoding="utf-8").split("\n")[0] == expected_content_first_line
    ), "First line of the content of the response didn't match with expected"


def test_get_data_from_path_with_one_distribution(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    f"""Test getting the actual data from a metadata with one distribution.
    Test for the path with distribution index: /{resource_name}/v1/1/data/0
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

    testing_get_path = default_path + "/0"
    expected_response_status_code = status.HTTP_200_OK
    expected_header_content_disposition = f"attachment; filename={filename}"
    expected_content_type = encoding_format
    expected_content_first_line = "time,battery,id,mag,mag_err,name,signal,tamb,tsky"

    # Add asset with no distributions
    response = client.post(
        f"/{resource_name}/v1", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    response = client.get(testing_get_path)

    assert response.status_code == expected_response_status_code, (
        f"The status code {response.status_code} didn't match with expected: "
        f"{expected_response_status_code}."
    )
    assert (
        response.headers.get("Content-Disposition") == expected_header_content_disposition
    ), "Content-Disposition of response doesn't match."

    assert (
        response.headers.get("Content-Type") == expected_content_type
    ), "Encoding format didn't match with expected"

    assert (
        str(response.content, encoding="utf-8").split("\n")[0] == expected_content_first_line
    ), "First line of the content of the response didn't match with expected"


def test_get_data_from_default_path_with_multiple_distributions(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    f"""Test getting the actual data from a metadata with multiple distributiona.
    Test for the default path (without distribution index): /{resource_name}/v1/1/data
    """

    keycloak_openid.userinfo = mocked_privileged_token

    with Session(engine) as session:
        session.add(person)
        session.commit()

    # Using same URL for both endpoints
    url_for_test = "https://zenodo.org/api/records/8206848/files/LPL11_July_2023.csv/content"
    filename0 = "LPL11_July_2023.csv"
    encoding_format0 = "text/csv"

    filename1 = "LPL11_July_2023_copy.txt"
    encoding_format1 = "text/txt"

    body = copy.deepcopy(body_asset)
    distribution = copy.deepcopy(body["distribution"][0])
    body["distribution"].append(distribution)

    body["distribution"][0]["content_url"] = url_for_test
    body["distribution"][0]["name"] = filename0
    body["distribution"][0]["encoding_format"] = encoding_format0

    body["distribution"][1]["content_url"] = url_for_test
    body["distribution"][1]["name"] = filename1
    body["distribution"][1]["encoding_format"] = encoding_format1

    testing_get_path = default_path
    expected_response_status_code = status.HTTP_200_OK
    expected_header_content_disposition = f"attachment; filename={filename0}"
    expected_content_type = encoding_format0
    expected_content_first_line = "time,battery,id,mag,mag_err,name,signal,tamb,tsky"

    # Add asset with multiple distributions
    response = client.post(
        f"/{resource_name}/v1", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    # Endpoint with index 0
    response0 = client.get(testing_get_path)

    assert response0.status_code == expected_response_status_code, (
        f"The status code {response0.status_code} didn't match with expected: "
        f"{expected_response_status_code} for {testing_get_path}."
    )
    assert (
        response0.headers.get("Content-Disposition") == expected_header_content_disposition
    ), f"Content-Disposition of response doesn't match for {testing_get_path}."

    assert (
        response0.headers.get("Content-Type") == expected_content_type
    ), f"Encoding format didn't match with expected for {testing_get_path}."

    assert str(response0.content, encoding="utf-8").split("\n")[0] == expected_content_first_line, (
        f"First line of the content of the response didn't match with expected"
        f"for {testing_get_path}."
    )


def test_get_data_from_path_with_multiple_distributions(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    f"""Test getting the actual data from a metadata with multiple distributiona.
    Test for the paths with distribution index:
        1. /{resource_name}/v1/1/data/0
        2. /{resource_name}/v1/1/data/1
    """

    keycloak_openid.userinfo = mocked_privileged_token

    with Session(engine) as session:
        session.add(person)
        session.commit()

    # Using same URL for both endpoints
    url_for_test = "https://zenodo.org/api/records/8206848/files/LPL11_July_2023.csv/content"
    filename0 = "LPL11_July_2023.csv"
    encoding_format0 = "text/csv"

    filename1 = "LPL11_July_2023_copy.txt"
    encoding_format1 = "text/txt"

    body = copy.deepcopy(body_asset)
    distribution = copy.deepcopy(body["distribution"][0])
    body["distribution"].append(distribution)

    body["distribution"][0]["content_url"] = url_for_test
    body["distribution"][0]["name"] = filename0
    body["distribution"][0]["encoding_format"] = encoding_format0

    body["distribution"][1]["content_url"] = url_for_test
    body["distribution"][1]["name"] = filename1
    body["distribution"][1]["encoding_format"] = encoding_format1

    testing_get_path_0 = default_path + "/0"
    expected_response_status_code0 = status.HTTP_200_OK
    expected_header_content_disposition0 = f"attachment; filename={filename0}"
    expected_content_type0 = encoding_format0
    expected_content_first_line0 = "time,battery,id,mag,mag_err,name,signal,tamb,tsky"

    testing_get_path_1 = default_path + "/1"
    expected_response_status_code1 = status.HTTP_200_OK
    expected_header_content_disposition1 = f"attachment; filename={filename1}"
    expected_content_type1 = encoding_format1
    expected_content_first_line1 = "time,battery,id,mag,mag_err,name,signal,tamb,tsky"

    # Add asset with no distributions
    response = client.post(
        f"/{resource_name}/v1", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    # Endpoint with index 0
    response0 = client.get(testing_get_path_0)

    assert response0.status_code == expected_response_status_code0, (
        f"The status code {response0.status_code} didn't match with expected: "
        f"{expected_response_status_code0} for {testing_get_path_0}."
    )
    assert (
        response0.headers.get("Content-Disposition") == expected_header_content_disposition0
    ), f"Content-Disposition of response doesn't match for {testing_get_path_0}."

    assert (
        response0.headers.get("Content-Type") == expected_content_type0
    ), f"Encoding format didn't match with expected for {testing_get_path_0}."

    assert (
        str(response0.content, encoding="utf-8").split("\n")[0] == expected_content_first_line0
    ), (
        f"First line of the content of the response didn't match with expected"
        f"for {testing_get_path_0}."
    )

    time.sleep(1)
    # Endpoint with index 1
    response1 = client.get(testing_get_path_1)

    assert response1.status_code == expected_response_status_code1, (
        f"The status code {response1.status_code} didn't match with expected: "
        f"{expected_response_status_code1} for {testing_get_path_1}."
    )
    assert (
        response1.headers.get("Content-Disposition") == expected_header_content_disposition1
    ), f"Content-Disposition of response doesn't match for {testing_get_path_1}."

    assert (
        response1.headers.get("Content-Type") == expected_content_type1
    ), f"Encoding format didn't match with expected for {testing_get_path_1}"

    assert (
        str(response1.content, encoding="utf-8").split("\n")[0] == expected_content_first_line1
    ), (
        "First line of the content of the response didn't match with expected"
        f"for {testing_get_path_1}."
    )


def test_get_data_out_of_range_from_path_with_multiple_distributions(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_asset: dict,
    person: Person,
):
    f"""Test getting the actual data from a metadata with multiple distributiona.
    Test for the path with distribution index out of range: /{resource_name}/v1/1/data/2
    """

    keycloak_openid.userinfo = mocked_privileged_token

    with Session(engine) as session:
        session.add(person)
        session.commit()

    # Using same URL for both endpoints
    url_for_test = "https://zenodo.org/api/records/8206848/files/LPL11_July_2023.csv/content"
    filename0 = "LPL11_July_2023.csv"
    encoding_format0 = "text/csv"

    filename1 = "LPL11_July_2023_copy.txt"
    encoding_format1 = "text/txt"

    body = copy.deepcopy(body_asset)
    distribution = copy.deepcopy(body["distribution"][0])
    body["distribution"].append(distribution)

    body["distribution"][0]["content_url"] = url_for_test
    body["distribution"][0]["name"] = filename0
    body["distribution"][0]["encoding_format"] = encoding_format0

    body["distribution"][1]["content_url"] = url_for_test
    body["distribution"][1]["name"] = filename1
    body["distribution"][1]["encoding_format"] = encoding_format1

    testing_get_path_2 = default_path + "/2"
    expected_response_status_code2 = status.HTTP_400_BAD_REQUEST
    expected_error_msg2 = "Distribution index out of range."

    # Add asset with multiple distributions
    response = client.post(
        f"/{resource_name}/v1", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    # Endpoint with index 2
    response0 = client.get(testing_get_path_2)

    assert response0.status_code == expected_response_status_code2, (
        f"The status code {response0.status_code} didn't match with expected: "
        f"{expected_response_status_code2} for {testing_get_path_2}."
    )
    assert (
        response0.json().get("detail") == expected_error_msg2
    ), f"Content-Disposition of response doesn't match for {testing_get_path_2}."
