import dataclasses
from requests.exceptions import HTTPError


@dataclasses.dataclass
class RecordError:
    identifier: str | None
    error: BaseException | HTTPError | str
    code: int | None = None
    ignore: bool = False
