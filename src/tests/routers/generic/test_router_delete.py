from unittest.mock import Mock

import pytest
from starlette.testclient import TestClient

from database.session import DbSession
from database.model.concept.aiod_entry import EntryStatus
from tests.testutils.test_resource import factory


@pytest.mark.parametrize("identifier", [1, 2])
def test_happy_path(
    client_test_resource: TestClient,
    identifier: int,
    mocked_privileged_token: Mock,
):
    with DbSession() as session:
        session.add_all(
            [
                factory(
                    title="my_test_resource",
                    platform="example",
                    platform_resource_identifier=1,
                    status=EntryStatus.DRAFT,
                ),
                factory(
                    title="second_test_resource",
                    platform="example",
                    platform_resource_identifier=2,
                    status=EntryStatus.DRAFT,
                ),
            ]
        )
        session.commit()
    response = client_test_resource.delete(
        f"/test_resources/v0/{identifier}", headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 200, response.json()
    response = client_test_resource.get("/test_resources/v0/")
    assert response.status_code == 200, response.json()
    response_json = response.json()
    assert len(response_json) == 1
    assert {r["identifier"] for r in response_json} == {1, 2} - {identifier}


@pytest.mark.parametrize("identifier", [3, 4])
def test_non_existent(
    client_test_resource: TestClient,
    identifier: int,
    mocked_privileged_token: Mock,
):
    with DbSession() as session:
        session.add_all(
            [
                factory(
                    title="my_test_resource",
                    platform="example",
                    platform_resource_identifier=1,
                    status=EntryStatus.DRAFT,
                ),
                factory(
                    title="second_test_resource",
                    platform="example",
                    platform_resource_identifier=2,
                    status=EntryStatus.DRAFT,
                ),
            ]
        )
        session.commit()
    response = client_test_resource.delete(
        f"/test_resources/v0/{identifier}", headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 404, response.json()
    assert response.json()["detail"] == f"Test_resource '{identifier}' not found in the database."


def test_add_after_deletion(
    client_test_resource: TestClient,
    mocked_privileged_token: Mock,
):
    body = {"title": "my_favourite_resource"}
    response = client_test_resource.post(
        "/test_resources/v0", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 200, response.json()
    id_ = response.json()["identifier"]
    response = client_test_resource.delete(
        f"/test_resources/v0/{id_}", headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 200, response.json()
    response = client_test_resource.post(
        "/test_resources/v0", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 200, response.json()
