import dataclasses


@dataclasses.dataclass
class RecordError:
    platform: str
    id: str
    type: str
    error: str
