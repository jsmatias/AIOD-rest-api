import copy
from unittest.mock import Mock

from sqlalchemy.engine import Engine
from sqlmodel import Session
from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model.agent.person import Person


def test_happy_path(
    client: TestClient,
    engine: Engine,
    mocked_privileged_token: Mock,
    body_agent: dict,
    person: Person,
):
    keycloak_openid.userinfo = mocked_privileged_token

    with Session(engine) as session:
        person.platform_identifier = "2"
        session.add(person)
        session.commit()

    body = copy.copy(body_agent)
    body["expertise"] = ["machine learning"]
    body["language"] = ["eng", "nld"]
    body["contact"] = [1]
    body["price_per_hour_euro"] = 10.50
    body["wants_to_be_contacted"] = True
    response = client.post("/persons/v1", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/persons/v1/2")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["identifier"] == 2
    assert response_json["ai_resource_identifier"] == 2
    assert response_json["agent_identifier"] == 2
    assert response_json["contact"] == [1]

    assert set(response_json["expertise"]) == {"machine learning"}
    assert set(response_json["language"]) == {"eng", "nld"}

    assert response_json["price_per_hour_euro"] == 10.50
    assert response_json["wants_to_be_contacted"]
