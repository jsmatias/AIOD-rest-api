import abc
import datetime
import logging
from typing import Generic, Iterator, TypeVar
from connectors.abstract.resource_connector import ResourceConnector
from connectors.record_error import RecordError

from sqlmodel import SQLModel

from connectors.resource_with_relations import ResourceWithRelations

RESOURCE = TypeVar("RESOURCE", bound=SQLModel)


class ResourceConnectorOnStartUp(ResourceConnector, Generic[RESOURCE]):
    """A connector that only runs once, on startup, and performs no synchronization later."""

    @abc.abstractmethod
    def fetch(
        self, limit: int | None = None
    ) -> Iterator[SQLModel | ResourceWithRelations[SQLModel] | RecordError]:
        """Retrieve information of all resources"""

    def run(
        self, state: dict, limit: int | None = None, **kwargs
    ) -> Iterator[SQLModel | ResourceWithRelations[SQLModel] | RecordError]:
        if state:
            raise ValueError("This connector has already been run before.")
        if limit is not None:
            logging.warning(
                "Limiting the results! Please remove the limit command line argument "
                "in production."
            )
        state["result"] = f"started on {datetime.datetime.now()}"
        yield from self.fetch(limit=limit)
        state["result"] = "complete run successful"
