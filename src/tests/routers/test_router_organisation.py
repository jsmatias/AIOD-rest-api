from unittest.mock import Mock

from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from authentication import keycloak_openid
from database.model.agent_table import AgentTable
from database.model.organisation.organisation import Organisation


def test_happy_path(client: TestClient, engine: Engine, mocked_privileged_token: Mock):
    keycloak_openid.userinfo = mocked_privileged_token

    with Session(engine) as session:
        session.add_all(
            [
                AgentTable(type="organisation"),
                Organisation(
                    identifier="1",
                    platform="example",
                    platform_identifier="2",
                    type="Research Institution ",
                ),
            ]
        )
        session.commit()

    body = {
        "platform": "zenodo",
        "platform_identifier": "2",
        "type": "Research Insititution",
        "connection_to_ai": "Example positioning in European AI ecosystem.",
        "logo_url": "aiod.eu/project/0/logo",
        "same_as": "https://www.example.com/organisation/example",
        "founding_date": "2022-01-01T15:15:00.000Z",
        "dissolution_date": "2023-01-01T15:15:00.000Z",
        "legal_name": "Example official name",
        "alternate_name": "Example alternate name",
        "address": "Example address",
        "telephone": "Example telephone number",
        "parent_organisation": 1,
        "business_categories": ["business category 1", "business category 2"],
        "technical_categories": ["technical category 1", "technical category 2"],
        "emails": ["email@org.com", "ceo@org.com"],
        "members": [1],
        "departments": [1],
    }

    response = client.post("/organisations/v0", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/organisations/v0/2")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["identifier"] == 2
    assert response_json["platform"] == "zenodo"
    assert "parent_organisation_id" not in response_json
    assert response_json["parent_organisation"] == 1
    assert set(response_json["business_categories"]) == {
        "business category 1",
        "business category 2",
    }
    assert set(response_json["technical_categories"]) == {
        "technical category 1",
        "technical category 2",
    }
    assert set(response_json["emails"]) == {"email@org.com", "ceo@org.com"}
    assert set(response_json["members"]) == {1}
    assert set(response_json["departments"]) == {1}

    response = client.delete("/organisations/v0/2", headers={"Authorization": "Fake token"})
    assert (
        response.status_code == 400
    ), response.json()  # you cannot delete the parent of other resources
    body["departments"] = []
    response = client.put("organisations/v0/2", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()
    response = client.delete("/organisations/v0/2", headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()
