from contextlib import contextmanager
from unittest.mock import Mock

import pytest
import responses
from fastapi import HTTPException
from keycloak import KeycloakError
from starlette import status

from authentication import get_current_user, keycloak_openid
from tests.testutils.authentication import MockedKeycloak, TestUserType


@contextmanager
def Jos() -> responses.RequestsMock:
    request_mock = responses.RequestsMock()
    try:
        yield request_mock
    finally:
        request_mock.__exit__(None, None, None)


@pytest.mark.asyncio
async def test_happy_path():
    with MockedKeycloak() as _:
        user = await get_current_user(token="Bearer mocked")
    assert user.name == "user"
    assert set(user.roles) == {"offline_access", "uma_authorization", "default-roles-aiod"}


@pytest.mark.asyncio
async def test_inactive_user():
    with MockedKeycloak(type_=TestUserType.inactive) as _:
        with pytest.raises(HTTPException) as exception_info:
            await get_current_user(token="Bearer mocked")

        assert exception_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exception_info.value.detail == "Invalid authentication token"


@pytest.mark.asyncio
async def test_unauthenticated():
    with pytest.raises(HTTPException) as exception_info:
        await get_current_user(token=None)
    assert exception_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        exception_info.value.detail
        == "This endpoint requires authorization. You need to be logged in."
    )


@pytest.mark.asyncio
async def test_keycloak_error():
    """
    On any problem, keycloak_openid.introspect raises an error.

    Refer to https://connect2id.com/products/server/docs/api/token-introspection for a list of
    possible errors. Only created a single testcase because we handle all errors the same way.
    """
    keycloak_openid.introspect = Mock(
        side_effect=KeycloakError(
            error_message="unused message", response_code=status.HTTP_403_FORBIDDEN
        )
    )
    with pytest.raises(HTTPException) as exception_info:
        await get_current_user(token="Bearer mocked")
    assert exception_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exception_info.value.detail == "Invalid authentication token"
