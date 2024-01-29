import traceback
from fastapi import HTTPException, status


def as_http_exception(exception: Exception) -> HTTPException:
    if isinstance(exception, HTTPException):
        return exception
    traceback.print_exc()
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=(
            "Unexpected exception while processing your request. Please contact the maintainers: "
            f"{exception}"
        ),
    )
