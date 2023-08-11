import copy
from unittest.mock import Mock

from sqlalchemy.engine import Engine
from starlette.testclient import TestClient

from authentication import keycloak_openid


def test_happy_path(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_agent: dict,
):
    keycloak_openid.userinfo = mocked_privileged_token

    body = copy.copy(body_agent)
    body["expertise"] = ["machine learning"]
    body["language"] = ["eng", "nld"]
    response = client.post("/persons/v0", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/persons/v0/1")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["identifier"] == 1
    assert response_json["resource_identifier"] == 1
    assert response_json["agent_identifier"] == 1

    assert set(response_json["expertise"]) == {"machine learning"}
    assert set(response_json["language"]) == {"eng", "nld"}
