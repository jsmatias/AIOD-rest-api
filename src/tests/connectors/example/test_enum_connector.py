from typing import TYPE_CHECKING

import pytest

from connectors.example.enum import EnumConnectorStatus

if TYPE_CHECKING:
    from connectors.example.example_connector import ExampleConnector  # noqa:F401

enum_connectors = {"status": EnumConnectorStatus()}


@pytest.mark.parametrize(
    "datatype",
    ["status"],
)
def test_fetch_happy_path(datatype: str):
    connector = enum_connectors[datatype]
    resources = list(connector.fetch())
    assert len(resources) >= 1
