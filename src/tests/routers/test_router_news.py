from unittest.mock import Mock

from starlette.testclient import TestClient

from authentication import keycloak_openid


def test_happy_path(client: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.userinfo = mocked_privileged_token
    body = {
        "platform": "example",
        "platform_identifier": "2",
        "title": "Example News",
        "date_modified": "2022-01-01T15:15:00.000Z",
        "body": "Example news body",
        "section": "Example news section",
        "headline": "Example news headline",
        "word_count": 100,
        "source": "https://news.source.example",
        "alternative_headline": "Example news alternative headline",
        "news_categories": ["news_category1", "news_category2"],
        "media": ["media1", "media2"],
        "keywords": ["keyword1", "keyword2"],
        "business_categories": ["business category 1", "business category 2"],
    }
    response = client.post("/news/v0", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()

    response = client.get("/news/v0/1")
    assert response.status_code == 200, response.json()

    response_json = response.json()
    assert response_json["identifier"] == 1
    assert response_json["platform"] == "example"
    assert response_json["platform_identifier"] == "2"
    assert response_json["title"] == "Example News"
    assert response_json["date_modified"] == "2022-01-01T15:15:00"
    assert response_json["body"] == "Example news body"
    assert response_json["section"] == "Example news section"
    assert response_json["headline"] == "Example news headline"
    assert response_json["section"] == "Example news section"
    assert response_json["word_count"] == 100
    assert response_json["source"] == "https://news.source.example"
    assert response_json["alternative_headline"] == "Example news alternative headline"
    assert set(response_json["news_categories"]) == {"news_category1", "news_category2"}
    assert set(response_json["media"]) == {"media1", "media2"}
    assert set(response_json["keywords"]) == {"keyword1", "keyword2"}
    assert set(response_json["business_categories"]) == {
        "business category 1",
        "business category 2",
    }
    response = client.delete("/news/v0/1", headers={"Authorization": "Fake token"})
    assert response.status_code == 200, response.json()
