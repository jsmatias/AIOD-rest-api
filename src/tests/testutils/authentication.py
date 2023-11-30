import enum
import json
from contextlib import contextmanager
from pathlib import Path

import responses

from tests.testutils.paths import path_test_resources


class TestUserType(enum.Enum):
    user = "user.json"
    privileged = "user_privileged.json"
    inactive = "user_inactive.json"


@contextmanager
def MockedKeycloak(type_: TestUserType = TestUserType.user) -> responses.RequestsMock:
    """
    Returning a SQLModel session bound to the (configured) database engine.

    Alternatively, we could have used FastAPI Depends, but that only works for FastAPI - while
    the synchronization, for instance, also needs a Session, but doesn't use FastAPI.
    """
    path_user = path_test_resources() / "authentication" / type_.value
    return _mocked_user(path_user)


def _mocked_user(path_user_json: Path) -> responses.RequestsMock:
    with path_user_json.open("r") as f:
        response = json.load(f)

    request_mock = responses.RequestsMock()
    request_mock.start()
    request_mock.add(
        responses.POST,
        "http://keycloak:8080/aiod-auth/realms/aiod/protocol/openid-connect/token/introspect",
        json=response,
    )
    try:
        yield request_mock
    finally:
        request_mock.__exit__(None, None, None)
