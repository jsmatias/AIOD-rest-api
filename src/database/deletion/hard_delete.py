import datetime
from datetime import timedelta
from typing import Type

from sqlalchemy import delete, and_
from sqlalchemy.engine import Engine
from sqlalchemy.sql.operators import is_not
from sqlmodel import Session

from database.model.concept.concept import AIoDConcept
from routers.parent_router import non_abstract_subclasses


def hard_delete_older_than(engine: Engine, age: timedelta):
    classes: list[Type[AIoDConcept]] = non_abstract_subclasses(AIoDConcept)
    date_threshold = datetime.datetime.now() - age
    with Session(engine) as session:
        for concept in classes:
            filter_ = and_(
                is_not(concept.date_deleted, None),
                concept.date_deleted < date_threshold,  # type: ignore
            )
            statement = delete(concept).where(filter_)
            session.exec(statement)
            session.commit()
