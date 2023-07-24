"""
Dataset is a complex resource, so they are tested separately.
"""

import typing  # noqa:F401 (flake8 raises incorrect 'Module imported but unused' error)
from unittest.mock import Mock

from starlette.testclient import TestClient

from authentication import keycloak_openid


def test_happy_path(client: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.userinfo = mocked_privileged_token

    body = {
        "platform": "example",
        "platform_identifier": "1",
        "name": "Example Presentation",
        "description": "A description.",
        "url": "https://example.com/presentation/example/description",
        "datePublished": "2022-01-01T15:15:00.000Z",
        "publisher": "John Doe",
        "author": "John Doe",
        "image": "https://example.com/presentation/example/image",
        "is_accessible_for_free": True,
    }
    response = client.post("/presentations/v0", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/presentations/v0/1")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["identifier"] == 1
    assert response_json["platform"] == "example"
    assert response_json["name"] == "Example Presentation"
    assert response_json["description"] == "A description."
    assert response_json["url"] == "https://example.com/presentation/example/description"
    assert response_json["datePublished"] == "2022-01-01T15:15:00"
    assert response_json["publisher"] == "John Doe"
    assert response_json["author"] == "John Doe"
    assert response_json["image"] == "https://example.com/presentation/example/image"
    assert response_json["is_accessible_for_free"]

    response = client.delete("/presentations/v0/1", headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()
