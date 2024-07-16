import copy
from unittest.mock import Mock

from starlette.testclient import TestClient

from authentication import keycloak_openid


def test_happy_path(
    client: TestClient,
    mocked_privileged_token: Mock,
    body_asset: dict,
):
    keycloak_openid.introspect = mocked_privileged_token
    body = copy.copy(body_asset)
    body["name"] = "Case Study"

    response = client.post("/case_studies/v1", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/case_studies/v1/1")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["name"] == "Case Study"
