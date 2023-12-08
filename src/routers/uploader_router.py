import abc

from fastapi import APIRouter


class UploaderRouter(abc.ABC):
    def create(self, url_prefix: str) -> APIRouter:
        router = APIRouter()

        return router
