import abc

from sqlalchemy.engine import Engine
from fastapi import APIRouter


class UploaderRouter(abc.ABC):
    def create(self, engine: Engine, url_prefix: str) -> APIRouter:
        router = APIRouter()

        return router
