import dataclasses


@dataclasses.dataclass
class RecordError:
    identifier: str | None
    error: BaseException | str
    ignore_error: bool = False
