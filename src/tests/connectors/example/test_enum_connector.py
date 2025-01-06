from connectors.example.enum import EnumConnectorEventMode


def test_fetch_happy_path():
    connector = EnumConnectorEventMode()
    resources = list(connector.fetch())

    allowed_modes = {"offline", "online", "hybrid"}
    assert set(resources) == allowed_modes
