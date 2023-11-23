import json

import responses

from connectors.openml.openml_mlmodel_connector import OpenMlMLModelConnector
from tests.testutils.paths import path_test_resources

OPENML_URL = "https://www.openml.org/api/v1/json"


def test_first_run():
    connector = OpenMlMLModelConnector(limit_per_iteration=2)
    with responses.RequestsMock() as mocked_requests:
        for offset in (0, 2):
            mock_list_data(mocked_requests, offset)
        for i in range(1, 4):
            mock_get_data(mocked_requests, str(i))

        mlmodels = list(connector.run(state={}, from_identifier=0, limit=None))

    assert {m.name for m in mlmodels} == {
        "openml.evaluation.EuclideanDistance",
        "openml.evaluation.PolynomialKernel",
        "openml.evaluation.RBFKernel",
    }
    assert len(mlmodels) == 3
    # add more assert statements


def test_second_run():
    connector = OpenMlMLModelConnector(limit_per_iteration=2)
    with responses.RequestsMock() as mocked_requests:
        mock_list_data(mocked_requests, offset=2)
        mock_get_data(mocked_requests, "3")
        mlmodels = list(
            connector.run(state={"offset": 2, "last_id": 2}, from_identifier=0, limit=None)
        )
    assert len(mlmodels) == 1
    assert {m.name for m in mlmodels} == {"openml.evaluation.RBFKernel"}


def test_second_run_wrong_identifier():
    connector = OpenMlMLModelConnector(limit_per_iteration=2)
    with responses.RequestsMock() as mocked_requests:
        mock_list_data(mocked_requests, offset=2)
        mock_get_data(mocked_requests, "3")
        mlmodels = list(
            connector.run(state={"offset": 2, "last_id": 0}, from_identifier=0, limit=None)
        )
    assert len(mlmodels) == 1
    assert {m.name for m in mlmodels} == {"openml.evaluation.RBFKernel"}


def mock_list_data(mocked_requests, offset):
    """
    Mocking requests to the OpenML dependency, so that we test only our own services
    """
    with open(
        path_test_resources() / "connectors" / "openml" / f"mlmodel_list_offset_{offset}.json",
        "r",
    ) as f:
        mlmodel_response = json.load(f)
    mocked_requests.add(
        responses.GET,
        f"{OPENML_URL}/flow/list/limit/2/offset/{offset}",
        json=mlmodel_response,
        status=200,
    )


def mock_get_data(mocked_requests: responses.RequestsMock, platform_resource_identifier: str):
    """
    Mocking requests to the OpenML dependency, so that we test only our own services
    """

    with open(
        path_test_resources()
        / "connectors"
        / "openml"
        / f"mlmodel_{platform_resource_identifier}.json",
        "r",
    ) as f:
        mlmodel_response = json.load(f)
    mocked_requests.add(
        responses.GET,
        f"{OPENML_URL}/flow/{platform_resource_identifier}",
        json=mlmodel_response,
        status=200,
    )
