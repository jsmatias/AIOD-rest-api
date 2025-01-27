"""
Test resource with router and mocked converter
"""

from typing import Type

from sqlmodel import Field

from database.model.concept.aiod_entry import AIoDEntryORM
from database.model.concept.concept import AIoDConcept, AIoDConceptBase
from database.model.concept.status import Status
from routers import ResourceRouter


class TestResourceBase(AIoDConceptBase):
    title: str = Field(max_length=250, nullable=False, unique=True)


class TestResource(TestResourceBase, AIoDConcept, table=True):  # type: ignore [call-arg]
    identifier: int = Field(default=None, primary_key=True)


def test_resource_factory(title=None, status=None, platform="example", platform_identifier="1"):
    if status is None:
        status = Status(name="draft")
    return TestResource(
        title=title,
        platform=platform,
        platform_identifier=platform_identifier,
        aiod_entry=AIoDEntryORM(status=status),
    )


class RouterTestResource(ResourceRouter):
    """Router with only "aiod" as possible output format, used only for unittests"""

    @property
    def version(self) -> int:
        return 0

    @property
    def resource_name(self) -> str:
        return "test_resource"

    @property
    def resource_name_plural(self) -> str:
        return "test_resources"

    @property
    def resource_class(self) -> Type[TestResource]:
        return TestResource
