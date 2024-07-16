from starlette.testclient import TestClient

from database.model.ai_asset.license import License
from database.model.dataset.dataset import Dataset
from database.model.knowledge_asset.publication import Publication
from database.session import DbSession


def test_happy_path(client: TestClient, dataset: Dataset, publication: Publication):

    dataset.license = License(name="license 1")
    publication.license = License(name="license 2")
    with DbSession() as session:
        session.add(dataset)
        session.merge(publication)
        session.commit()

    response = client.get("/licenses/v1")
    assert response.status_code == 200, response.json()
    response_json = response.json()
    assert set(response_json).issuperset({"license 1", "license 2"})
