import dataclasses


@dataclasses.dataclass
class RecordError:
    identifier: str | None
    error: BaseException | str
    code: int | None = None
    ignore: bool = False
