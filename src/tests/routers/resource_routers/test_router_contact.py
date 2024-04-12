import copy
from unittest.mock import Mock

from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model.agent.contact import Contact
from database.model.agent.email import Email
from database.session import DbSession


def test_email_privacy(
    client: TestClient,
    mocked_privileged_token: Mock,
    contact: Contact,
):
    keycloak_openid.introspect = mocked_privileged_token

    with DbSession() as session:
        email = Email(name="fake@email.com")
        another_email = Email(name="fake2@email.com")
        contact.email = [email, another_email]
        session.add(contact)
        session.commit()

    guest_response = client.get("/contacts/v1/")
    assert guest_response.status_code == 200, guest_response.json()
    guest_response_json = guest_response.json()
    assert len(guest_response_json) == 1
    assert guest_response_json[0]["email"] == ["******"]

    response = client.get("/contacts/v1/", headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["email"] == ["fake@email.com", "fake2@email.com"]


def test_happy_path(client: TestClient, mocked_privileged_token: Mock, body_asset: dict):
    keycloak_openid.introspect = mocked_privileged_token
    client.post(
        "/persons/v1", json={"name": "test person"}, headers={"Authorization": "Fake token"}
    )

    body = copy.deepcopy(body_asset)
    body["name"] = "Contact name"
    body["email"] = ["a@b.com"]
    body["telephone"] = ["0032 xxxx xxxx"]
    body["location"] = [
        {
            "address": {"country": "NED", "street": "Street Name 10", "postal_code": "1234AB"},
            "geo": {"latitude": 37.42242, "longitude": -122.08585, "elevation_millimeters": 2000},
        }
    ]
    body["person"] = 1

    response = client.post("/contacts/v1", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/contacts/v1/1", headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["name"] == "Contact name"
    assert response_json["email"] == ["a@b.com"]
    assert response_json["telephone"] == ["0032 xxxx xxxx"]
    assert response_json["location"] == [
        {
            "address": {"country": "NED", "street": "Street Name 10", "postal_code": "1234AB"},
            "geo": {"latitude": 37.42242, "longitude": -122.08585, "elevation_millimeters": 2000},
        }
    ]
    assert response_json["person"] == 1


def test_post_duplicate_email(
    client: TestClient,
    mocked_privileged_token: Mock,
):
    """
    It should be possible to add same email in different contacts, to enable
    """
    keycloak_openid.introspect = mocked_privileged_token

    body1 = {"email": ["a@example.com", "b@example.com"]}
    body2 = {"email": ["c@example.com", "b@example.com"]}
    response = client.post("/contacts/v1", json=body1, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()
    response = client.post("/contacts/v1", json=body2, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    contact = client.get("/contacts/v1/2", headers={"Authorization": "Fake token"}).json()
    assert set(contact["email"]) == {"b@example.com", "c@example.com"}
    body3 = {"email": ["d@example.com", "b@example.com"]}
    client.put("/contacts/v1/1", json=body3, headers={"Authorization": "Fake token"})
    contact = client.get("/contacts/v1/2", headers={"Authorization": "Fake token"}).json()
    msg = "changing emails of contact 1 should not change emails of contact 2."
    assert set(contact["email"]) == {"b@example.com", "c@example.com"}, msg


def test_person_and_organisation_both_specified(client: TestClient, mocked_privileged_token):
    keycloak_openid.introspect = mocked_privileged_token
    headers = {"Authorization": "Fake token"}
    client.post("/persons/v1", json={"name": "test person"}, headers=headers)
    client.post("/organisations/v1", json={"name": "test organisation"}, headers=headers)

    body = {"person": 1, "organisation": 1}
    response = client.post("/contacts/v1", json=body, headers=headers)
    assert response.status_code == 400, response.json()
    assert response.json()["detail"] == "Person and organisation cannot be both filled."
