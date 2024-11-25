import os
import json
import responses

from datetime import datetime

from connectors.aibuilder.aibuilder_mlmodel_connector import AIBuilderMLModelConnector
from connectors.aibuilder.aibuilder_mlmodel_connector import API_URL, TOKEN
from connectors.resource_with_relations import ResourceWithRelations
from database.model.models_and_experiments.ml_model import MLModel
from database.model.platform.platform_names import PlatformName
from tests.testutils.paths import path_test_resources
from database.model.ai_resource.text import Text

def test_fetch_happy_path():
    connector = AIBuilderMLModelConnector()
    test_resources_path = os.path.join(path_test_resources, "connectors", "aibuilder")
    catalog_list_path = os.path.join(test_resources_path, "catalog_list.json")
    catalog_list_url = f"{API_URL}/get_catalog_list?apiToken={TOKEN}"
    catalog_solutions_path = os.path.join(test_resources_path, "catalog_solutions.json")
    catalog_solutions_url = f"{API_URL}/get_catalog_solutions?catalogId=1&apiToken={TOKEN}"
    solution_1_path = os.path.join(test_resources_path, "solution_1.json")
    solution_1_url = f"{API_URL}/get_solution?fullId=1&apiToken={TOKEN}"
    solution_2_path = os.path.join(test_resources_path, "solution_2.json")
    solution_2_url = f"{API_URL}/get_solution?fullId=2&apiToken={TOKEN}"
    mocked_datetime_from = datetime.fromisoformat("2023-09-01T00:00:00Z")
    mocked_datetime_to = datetime.fromisoformat("2023-09-01T00:00:01Z")
    expected_resources = []
    fetched_resources = []
    with responses.RequestsMock() as mocked_requests:
        with open(catalog_list_path, 'r') as f:
            response = json.load(f)
        mocked_requests.add(responses.GET, catalog_list_url, json=response, status=200)
        with open(catalog_solutions_path, 'r') as f:
            response = json.load(f)
        mocked_requests.add(responses.GET, catalog_solutions_url, json=response, status=200)
        with open(solution_1_path, 'r') as f:
            response = json.load(f)
            expected_resources.append(response)
        mocked_requests.add(responses.GET, solution_1_url, json=response, status=200)
        with open(solution_2_path, 'r') as f:
            response = json.load(f)
            expected_resources.append(response)
        mocked_requests.add(responses.GET, solution_2_url, json=response, status=200)
        fetched_resources = list(connector.fetch(mocked_datetime_from, mocked_datetime_to))

    assert len(fetched_resources) == len(expected_resources)
    for i, (datetime, mlmodel) in enumerate(fetched_resources):
        assert datetime == mocked_datetime_from
        assert type(mlmodel) == ResourceWithRelations[MLModel]
        assert mlmodel.platform == PlatformName.aibuilder
        assert mlmodel.platform_resource_identifier == str(i)
        assert mlmodel.name == f"Mocking Full Solution {i}"
        assert mlmodel.date_published == "2023-09-01T00:00:00Z"
        assert mlmodel.description == Text(plain=f"The mocked full solution {i}.")
        assert set(mlmodel.keyword) == {f"Mocked tag {i}."}
        assert mlmodel.is_accessible_for_free
