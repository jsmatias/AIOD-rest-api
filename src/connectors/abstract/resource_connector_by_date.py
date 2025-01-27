import abc
import logging
from datetime import datetime, date
from typing import Generic, Iterator, Tuple
from connectors.abstract.resource_connector import ResourceConnector
from connectors.record_error import RecordError


from connectors.resource_with_relations import ResourceWithRelations
from routers.resource_router import RESOURCE


class ResourceConnectorByDate(ResourceConnector, Generic[RESOURCE]):
    """Connectors that synchronize by filtering the results on datetime. In every subsequent run,
    the previous end-datetime is used as datetime-from."""

    @abc.abstractmethod
    def retry(self, _id: int) -> RESOURCE | ResourceWithRelations[RESOURCE] | RecordError:
        """Retrieve information of the resource identified by id"""

    @abc.abstractmethod
    def fetch(
        self, from_incl: datetime, to_excl: datetime
    ) -> Iterator[Tuple[datetime | None, RESOURCE | ResourceWithRelations[RESOURCE] | RecordError]]:
        """Retrieve information of all resources"""

    def run(
        self,
        state: dict,
        from_date: date | None = None,
        limit: int | None = None,
        to_excl: datetime | None = None,
        **kwargs,
    ) -> Iterator[RESOURCE | ResourceWithRelations[RESOURCE] | RecordError]:
        if limit is not None:
            raise ValueError(
                "Limit not implemented for this connector. Please remove the command "
                "line argument."
            )
        if to_excl is not None:
            logging.warning("to_excl should only be set in (unit) tests")
        else:
            to_excl = datetime.now()

        first_run = not state
        if first_run:
            if from_date is None:
                raise ValueError("In the first run, the from-date needs to be set")
            from_incl = datetime.combine(from_date, datetime.min.time())
        else:
            from_incl = datetime.fromtimestamp(state["last"] + 0.001)

        logging.info(f"Starting synchronisation {from_incl=}, {to_excl=}.")
        state["from_incl"] = from_incl.timestamp()
        state["to_excl"] = to_excl.timestamp()
        for datetime_, result in self.fetch(from_incl=from_incl, to_excl=to_excl):
            yield result
            if datetime_:
                state["last"] = datetime_.timestamp()
        state["result"] = "Complete run done (although there might be errors)."
