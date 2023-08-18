from unittest.mock import Mock
from starlette.testclient import TestClient

from authentication import keycloak_openid


def test_happy_path(client: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.userinfo = mocked_privileged_token

    body = {
        "platform": "zenodo",
        "platform_identifier": "1",
        "description": "A description.",
        "name": "Example Case Study",
        "creator": "John Doe",
        "publisher": "John Doe",
        "date_modified": "2023-01-01T15:15:00.000Z",
        "date_published": "2022-01-01T15:15:00.000Z",
        "same_as": "https://www.example.com/case_study/example",
        "url": "aiod.eu/case_study/0",
        "is_accessible_for_free": True,
        "alternate_names": ["alias 1", "alias 2"],
        "keywords": ["keyword1", "keyword2"],
        "business_categories": ["business category 1", "business category 2"],
        "technical_categories": ["technical category 1", "technical category 2"],
    }

    response = client.post("/case_studies/v0", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/case_studies/v0/1")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["identifier"] == 1

    assert response_json["url"] == "aiod.eu/case_study/0"
    assert response_json["description"] == "A description."

    assert set(response_json["alternate_names"]) == {"alias 1", "alias 2"}
    assert set(response_json["keywords"]) == {"keyword1", "keyword2"}
    assert set(response_json["business_categories"]) == {
        "business category 1",
        "business category 2",
    }
    assert set(response_json["technical_categories"]) == {
        "technical category 1",
        "technical category 2",
    }
    response = client.delete("/case_studies/v0/1", headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()
