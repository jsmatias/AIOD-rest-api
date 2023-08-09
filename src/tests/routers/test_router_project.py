from unittest.mock import Mock

import pytest
from starlette.testclient import TestClient

from authentication import keycloak_openid


@pytest.mark.skip(reason="TODO: while going to Metadata model v2")
def test_happy_path(client: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.userinfo = mocked_privileged_token

    body = {
        "platform": "zenodo",
        "platform_identifier": "1",
        "name": "Example Project",
        "doi": "0000000/000000000000",
        "start_date": "2022-01-01T15:15:00.000Z",
        "end_date": "2023-01-01T15:15:00.000Z",
        "founded_under": "John Doe",
        "total_cost_euro": 100000000.54,
        "eu_contribution_euro": 100000000.54,
        "coordinated_by": "John Doe",
        "project_description_title": "A project description title",
        "project_description_text": "Example project description",
        "programmes_url": "aiod.eu/project/0/programme",
        "topic_url": "aiod.eu/project/0/topic",
        "call_for_proposal": "Example call for proposal",
        "founding_scheme": "founding scheme",
        "image": "Example image",
        "url": "aiod.eu/project/0",
        "keywords": ["keyword1", "keyword2"],
        "identifier": 1,
    }

    response = client.post("/projects/v0", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/projects/v0/1")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["platform_identifier"] == "1"
    assert response_json["name"] == "Example Project"
    assert response_json["identifier"] == 1
    assert response_json["total_cost_euro"] == 100000000.54
    assert response_json["url"] == "aiod.eu/project/0"

    assert set(response_json["keywords"]) == {"keyword1", "keyword2"}

    response = client.delete("/projects/v0/1", headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()
