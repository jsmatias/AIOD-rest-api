import copy
from unittest.mock import Mock

from sqlalchemy.engine import Engine
from starlette.testclient import TestClient

from authentication import keycloak_openid


def test_happy_path(
    client: TestClient, engine: Engine, mocked_privileged_token: Mock, body_asset: dict
):
    keycloak_openid.userinfo = mocked_privileged_token
    body = copy.copy(body_asset)
    response = client.post("/datasets/v0", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/datasets/v0/1")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["identifier"] == 1
    assert response_json["resource_identifier"] == 1
    assert response_json["asset_identifier"] == 1

    assert response_json["aiod_entry"]["platform"] == "example"
    assert response_json["aiod_entry"]["platform_identifier"] == "1"
    assert response_json["aiod_entry"]["status"] == "draft"

    assert response_json["name"] == "The name"
    assert response_json["description"] == "A description."
    assert set(response_json["alternate_name"]) == {"alias1", "alias2"}
    assert set(response_json["keyword"]) == {"tag1", "tag2"}

    assert response_json["application_area"] == ["Voice Assistance"]
    assert response_json["industrial_sector"] == ["eCommerce"]
    assert response_json["research_area"] == ["Explainable AI"]
    assert response_json["scientific_domain"] == ["Voice Recognition"]

    (media,) = response_json["media"]
    assert media["name"] == "Resource logo"
    assert media["content_url"] == "https://www.example.com/resource.png"

    (distribution,) = response_json["distribution"]
    assert distribution["name"] == "downloadable instance of this resource"
    assert distribution["content_url"] == "https://www.example.com/resource.pdf"

    assert response_json["version"] == "1.a"

    body["aiod_entry"]["platform_identifier"] = "2"
    body["name"] = "new name"
    body["version"] = "1.b"
    body["distribution"] = [
        {
            "name": "downloadable instance of this resource",
            "content_url": "https://www.example.com/resource_new.pdf",
        }
    ]

    response = client.put("/datasets/v0/1", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/datasets/v0/1")
    response_json = response.json()
    assert response_json["identifier"] == 1
    assert response_json["resource_identifier"] == 1
    assert response_json["asset_identifier"] == 1

    assert response_json["aiod_entry"]["platform"] == "example"
    assert response_json["aiod_entry"]["platform_identifier"] == "2"

    assert response_json["name"] == "new name"

    (distribution,) = response_json["distribution"]
    assert distribution["name"] == "downloadable instance of this resource"
    assert distribution["content_url"] == "https://www.example.com/resource_new.pdf"

    assert response_json["version"] == "1.b"

    # TODO: test delete
