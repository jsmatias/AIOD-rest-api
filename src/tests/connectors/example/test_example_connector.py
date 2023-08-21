import pytest
from connectors import example_connectors


@pytest.mark.parametrize(
    "datatype",
    [
        "datasets",
        "experiments",
        "ml_models",
        "organisations",
        "persons",
        "publications",
        "services",
    ],
)
def test_fetch_happy_path(datatype: str):
    connector = example_connectors[datatype]
    resources = list(connector.fetch())
    assert len(resources) >= 1
    resource = resources[0]
    if hasattr(resource, "keywords"):  # otherwise, only tested that connector can run
        assert set(resource.keywords) == {"keyword1", "keyword2"}
