import dataclasses


@dataclasses.dataclass
class RecordError:
    platform: str
    _id: str
    type: str
    error: str
