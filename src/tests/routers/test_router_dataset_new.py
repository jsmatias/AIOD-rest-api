from unittest.mock import Mock

from sqlalchemy.engine import Engine
from starlette.testclient import TestClient

from authentication import keycloak_openid


def test_happy_path(client: TestClient, engine: Engine, mocked_privileged_token: Mock):
    keycloak_openid.userinfo = mocked_privileged_token

    body = {"name": "Example Dataset", "keywords": ["keyword1", "keyword2"], "version": "1.a"}
    response = client.post("/datasets_new/v0", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/datasets_new/v0/1")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["identifier"] == 1
    assert response_json["name"] == "Example Dataset"
    assert response_json["resource_identifier"] == 1
    assert response_json["version"] == "1.a"
    assert set(response_json["keywords"]) == {"keyword1", "keyword2"}

    body_put = {
        "name": "Changed name",
        "keywords": ["keyword2", "keyword3"],
        "identifier": 1,
        "resource_identifier": 1,
        "version": "1.b",
    }
    response = client.put(
        "/datasets_new/v0/1", json=body_put, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 200, response.json()

    response = client.get("/datasets_new/v0/1")
    response_json = response.json()
    assert response.status_code == 200, response.json()
    assert response_json["identifier"] == 1
    assert response_json["name"] == "Changed name"
    assert set(response_json["keywords"]) == {"keyword2", "keyword3"}
    assert response_json["resource_identifier"] == 1
    assert response_json["version"] == "1.b"

    # TODO: test delete
