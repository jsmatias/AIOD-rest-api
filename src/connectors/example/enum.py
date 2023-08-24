import pathlib

from connectors.example.enum_fill_connector import EnumConnector
from database.model.concept.status import Status

ENUM_PATH = pathlib.Path(__file__).parent.parent / "example" / "resources" / "enum"


class EnumConnectorStatus(EnumConnector[Status]):
    def __init__(self):
        json_path = ENUM_PATH / "status.json"
        super().__init__(json_path, Status)
