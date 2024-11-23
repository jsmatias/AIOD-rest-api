import copy
from unittest.mock import Mock

from starlette.testclient import TestClient


def test_happy_path(
    client: TestClient,
    mocked_privileged_token: Mock,
    body_resource: dict,
):
    body = copy.copy(body_resource)
    body["slogan"] = "Smart Blockchains for everyone!"
    body["terms_of_service"] = "Some text here"
    response = client.post("/services/v1", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/services/v1/1")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["identifier"] == 1
    assert response_json["ai_resource_identifier"] == 1

    assert response_json["slogan"] == "Smart Blockchains for everyone!"
    assert response_json["terms_of_service"] == "Some text here"
