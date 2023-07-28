from sqlalchemy.future import Engine
from sqlmodel import Session
from starlette.testclient import TestClient

from database.model import AIAssetTable
from tests.testutils.test_resource import TestResource


def test_get_count_happy_path(client_test_resource: TestClient, engine_test_resource: Engine):
    with Session(engine_test_resource) as session:
        session.add_all(
            [
                AIAssetTable(type="test_resource"),
                AIAssetTable(type="test_resource"),
                TestResource(title="my_test_resource_1"),
                TestResource(title="My second test resource"),
            ]
        )
        session.commit()
    response = client_test_resource.get("/counts/test_resources/v0")
    assert response.status_code == 200, response.json()
    response_json = response.json()

    assert response_json == 2
    assert "deprecated" not in response.headers
