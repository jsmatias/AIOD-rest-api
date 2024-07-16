from unittest.mock import Mock

import pytest
from starlette.testclient import TestClient

from authentication import keycloak_openid


@pytest.mark.parametrize(
    "title",
    ["\"'é:?", "!@#$%^&*()`~", "Ω≈ç√∫˜µ≤≥÷", "田中さんにあげて下さい", " أي بعد, ", "𝑻𝒉𝒆 𝐪𝐮𝐢𝐜𝐤", "گچپژ"],
)
def test_unicode(client_test_resource: TestClient, title: str, mocked_privileged_token: Mock):
    keycloak_openid.introspect = mocked_privileged_token
    response = client_test_resource.post(
        "/test_resources/v0",
        json={"title": title, "platform": "example", "platform_resource_identifier": "1"},
        headers={"Authorization": "Fake token"},
    )
    assert response.status_code == 200, response.json()
    assert response.json() == {"identifier": 1}
    response = client_test_resource.get("/test_resources/v0/1")
    assert response.status_code == 200, response.json()
    response_json = response.json()
    assert response_json["title"] == title


def test_missing_value(client_test_resource: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.introspect = mocked_privileged_token
    body = {"platform": "example", "platform_resource_identifier": "1"}
    response = client_test_resource.post(
        "/test_resources/v0", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 422, response.json()
    assert response.json()["detail"] == [
        {"loc": ["body", "title"], "msg": "field required", "type": "value_error.missing"}
    ]


def test_null_value(client_test_resource: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.introspect = mocked_privileged_token
    body = {"title": None, "platform": "example", "platform_resource_identifier": "1"}
    response = client_test_resource.post(
        "/test_resources/v0", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 422, response.json()
    assert response.json()["detail"] == [
        {
            "loc": ["body", "title"],
            "msg": "none is not an allowed value",
            "type": "type_error.none.not_allowed",
        }
    ]


def test_posting_same_item_twice(client_test_resource: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.introspect = mocked_privileged_token
    headers = {"Authorization": "Fake token"}
    body = {"title": "title1", "platform": "example", "platform_resource_identifier": "1"}
    response = client_test_resource.post("/test_resources/v0", json=body, headers=headers)
    assert response.status_code == 200, response.json()
    body = {"title": "title2", "platform": "example", "platform_resource_identifier": "1"}
    response = client_test_resource.post("/test_resources/v0", json=body, headers=headers)
    assert response.status_code == 409, response.json()
    assert (
        response.json()["detail"] == "There already exists a test_resource with the same "
        "platform and platform_resource_identifier, with identifier=1."
    )


def test_posting_same_item_twice_but_deleted(
    client_test_resource: TestClient, mocked_privileged_token: Mock
):
    keycloak_openid.introspect = mocked_privileged_token
    headers = {"Authorization": "Fake token"}
    body = {"title": "title1", "platform": "example", "platform_resource_identifier": "1"}
    response = client_test_resource.post("/test_resources/v0", json=body, headers=headers)
    assert response.status_code == 200, response.json()

    response = client_test_resource.delete("/test_resources/v0/1", headers=headers)
    assert response.status_code == 200, response.json()

    body = {"title": "title2", "platform": "example", "platform_resource_identifier": "1"}
    response = client_test_resource.post("/test_resources/v0", json=body, headers=headers)
    assert response.status_code == 200, response.json()


def test_no_platform_no_platform_resource_identifier(
    client_test_resource: TestClient, mocked_privileged_token: Mock
):
    keycloak_openid.introspect = mocked_privileged_token
    headers = {"Authorization": "Fake token"}
    body = {"title": "title1", "platform": None, "platform_resource_identifier": None}
    response = client_test_resource.post("/test_resources/v0", json=body, headers=headers)
    assert response.status_code == 200, response.json()
    body = {"title": "title2", "platform": None, "platform_resource_identifier": None}
    response = client_test_resource.post("/test_resources/v0", json=body, headers=headers)
    assert response.status_code == 200, response.json()


def test_no_platform_with_platform_resource_identifier(
    client_test_resource: TestClient, mocked_privileged_token: Mock
):
    keycloak_openid.introspect = mocked_privileged_token
    headers = {"Authorization": "Fake token"}
    body = {"title": "title1", "platform": None, "platform_resource_identifier": "1"}
    response = client_test_resource.post("/test_resources/v0", json=body, headers=headers)
    assert response.status_code == 400, response.json()
    assert (
        response.json()["detail"]
        == "If platform is NULL, platform_resource_identifier should also be "
        "NULL, and vice versa."
    )


def test_platform_with_no_platform_resource_identifier(
    client_test_resource: TestClient, mocked_privileged_token: Mock
):
    keycloak_openid.introspect = mocked_privileged_token
    headers = {"Authorization": "Fake token"}
    body = {"title": "title1", "platform": "example", "platform_resource_identifier": None}
    response = client_test_resource.post("/test_resources/v0", json=body, headers=headers)
    assert response.status_code == 400, response.json()
    assert (
        response.json()["detail"]
        == "If platform is NULL, platform_resource_identifier should also be "
        "NULL, and vice versa."
    )


def test_non_existent_platform(client_test_resource: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.introspect = mocked_privileged_token
    keycloak_openid.public_key = Mock(return_value="")
    headers = {"Authorization": "Fake token"}
    body = {"title": "title1", "platform": "this_does_not_exist", "platform_resource_identifier": 1}
    response = client_test_resource.post("/test_resources/v0", json=body, headers=headers)
    assert response.status_code == 412
    assert (
        response.json()["detail"] == "Platform this_does_not_exist does not exist. You can "
        "register it using the POST platforms endpoint."
    )
