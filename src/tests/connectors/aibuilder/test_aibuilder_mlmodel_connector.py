import os
import json
import responses

from datetime import datetime
from requests.exceptions import HTTPError

from connectors.aibuilder.aibuilder_mlmodel_connector import AIBuilderMLModelConnector
from connectors.aibuilder.aibuilder_mlmodel_connector import API_URL, TOKEN
from connectors.resource_with_relations import ResourceWithRelations
from connectors.record_error import RecordError
from database.model.models_and_experiments.ml_model import MLModel
from database.model.platform.platform_names import PlatformName
from tests.testutils.paths import path_test_resources
from database.model.ai_resource.text import Text

connector = AIBuilderMLModelConnector()
test_resources_path = os.path.join(path_test_resources(), "connectors", "aibuilder")
catalog_list_url = f"{API_URL}/get_catalog_list?apiToken={TOKEN}"
mocked_datetime_from = datetime.fromisoformat("2023-09-01T00:00:00Z")
mocked_datetime_to = datetime.fromisoformat("2023-09-01T00:00:01Z")


def test_fetch_happy_path():
    catalog_list_path = os.path.join(test_resources_path, "catalog_list.json")
    catalog_solutions_path = os.path.join(test_resources_path, "catalog_solutions.json")
    catalog_solutions_url = f"{API_URL}/get_catalog_solutions?catalogId=1&apiToken={TOKEN}"
    solution_1_path = os.path.join(test_resources_path, "solution_1.json")
    solution_1_url = f"{API_URL}/get_solution?fullId=1&apiToken={TOKEN}"
    solution_2_path = os.path.join(test_resources_path, "solution_2.json")
    solution_2_url = f"{API_URL}/get_solution?fullId=2&apiToken={TOKEN}"
    expected_resources = []
    fetched_resources = []
    with responses.RequestsMock() as mocked_requests:
        with open(catalog_list_path, "r") as f:
            response = json.load(f)
        mocked_requests.add(responses.GET, catalog_list_url, json=response, status=200)
        with open(catalog_solutions_path, "r") as f:
            response = json.load(f)
        mocked_requests.add(responses.GET, catalog_solutions_url, json=response, status=200)
        with open(solution_1_path, "r") as f:
            response = json.load(f)
            expected_resources.append(response)
        mocked_requests.add(responses.GET, solution_1_url, json=response, status=200)
        with open(solution_2_path, "r") as f:
            response = json.load(f)
            expected_resources.append(response)
        mocked_requests.add(responses.GET, solution_2_url, json=response, status=200)
        fetched_resources = list(connector.fetch(mocked_datetime_from, mocked_datetime_to))

    assert len(fetched_resources) == len(expected_resources)
    for i, (last_modified, resource) in enumerate(fetched_resources):
        assert last_modified == mocked_datetime_from
        assert type(resource) == ResourceWithRelations
        assert resource.resource_ORM_class == MLModel
        assert resource.resource.platform == PlatformName.aibuilder
        assert resource.resource.platform_resource_identifier == str(i + 1)
        assert resource.resource.name == f"Mocking Full Solution {i + 1}"
        assert resource.resource.date_published == mocked_datetime_from
        assert resource.resource.description == Text(plain=f"The mocked full solution {i + 1}.")
        assert set(resource.resource.keyword) == {f"Mocked tag {i + 1}."}
        assert resource.resource.is_accessible_for_free


def test_catalog_list_http_error():
    error = {"error": {"message": "HTTP Error."}}
    err_msg = f"Error while fetching {catalog_list_url} from AIBuilder: (500) HTTP Error."
    fetched_resources = []
    with responses.RequestsMock() as mocked_requests:
        mocked_requests.add(responses.GET, catalog_list_url, json=error, status=500)
        fetched_resources = list(connector.fetch(mocked_datetime_from, mocked_datetime_to))

    assert len(fetched_resources) == 1
    last_modified, resource = fetched_resources[0]
    assert last_modified is None
    assert type(resource) == RecordError
    assert resource.identifier is None
    assert type(resource.error) == HTTPError
    assert str(resource.error) == err_msg


def test_catalog_list_format_error():
    catalog_list_path = os.path.join(test_resources_path, "catalog_list_format_error.json")
    fetched_resources = []
    with responses.RequestsMock() as mocked_requests:
        with open(catalog_list_path, "r") as f:
            response = json.load(f)
        mocked_requests.add(responses.GET, catalog_list_url, json=response, status=200)
        fetched_resources = list(connector.fetch(mocked_datetime_from, mocked_datetime_to))

    assert len(fetched_resources) == 1
    last_modified, resource = fetched_resources[0]
    assert last_modified is None
    assert type(resource) == RecordError
    assert resource.identifier is None
    assert type(resource.error) == KeyError
    assert str(resource.error) == "'catalogId'"


def test_empty_catalog_list():
    catalog_list_path = os.path.join(test_resources_path, "empty_catalog_list.json")
    fetched_resources = []
    with responses.RequestsMock() as mocked_requests:
        with open(catalog_list_path, "r") as f:
            response = json.load(f)
        mocked_requests.add(responses.GET, catalog_list_url, json=response, status=200)
        fetched_resources = list(connector.fetch(mocked_datetime_from, mocked_datetime_to))

    assert len(fetched_resources) == 1
    last_modified, resource = fetched_resources[0]
    assert last_modified is None
    assert type(resource) == RecordError
    assert resource.identifier is None
    assert resource.error == "Empty catalog list."
