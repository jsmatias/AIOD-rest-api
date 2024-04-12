from typing import Sequence
from sqlmodel import Session
from database.model.agent.person import Person
from routers.resource_router import Pagination, ResourceRouter
from authentication import User


class PersonRouter(ResourceRouter):
    @property
    def version(self) -> int:
        return 1

    @property
    def resource_name(self) -> str:
        return "person"

    @property
    def resource_name_plural(self) -> str:
        return "persons"

    @property
    def resource_class(self) -> type[Person]:
        return Person

    @staticmethod
    def _verify_user_roles(person: type[Person], user: User | None) -> type[Person]:
        """
        Only users with role 'full_view_drupal_resources' can see sensitive
        of a person from the old drupal platform.
        """
        if (person.platform == "drupal") and not (
            user and user.has_role("full_view_drupal_resources")
        ):
            person.name = "******"
            person.given_name = "******"
            person.surname = "******"
        return person

    def _retrieve_resource(
        self,
        session: Session,
        identifier: int | str,
        user: User | None = None,
        platform: str | None = None,
    ) -> type[Person]:
        person: type[Person] = super()._retrieve_resource(session, identifier, user, platform)
        return self._verify_user_roles(person, user)

    def _retrieve_resources(
        self,
        session: Session,
        pagination: Pagination,
        user: User | None = None,
        platform: str | None = None,
    ) -> Sequence[type[Person]]:
        persons: Sequence[type[Person]] = super()._retrieve_resources(
            session, pagination, user, platform
        )
        persons = [self._verify_user_roles(person, user) for person in persons]
        return persons
