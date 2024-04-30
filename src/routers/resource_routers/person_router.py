from typing import Sequence
from sqlmodel import Session
from database.model.agent.person import Person
from routers.resource_router import ResourceRouter
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
    def _post_process(
        resources: Sequence[type[Person]], session: Session, user: User | None
    ) -> Sequence[type[Person]]:
        """
        For the old drupal platform, only users with "full_view_drupal_resources" role can
        see the person's sensitive information.
        """
        persons = []
        for person in resources:
            if (person.platform == "drupal") and not (
                user and user.has_role("full_view_drupal_resources")
            ):
                person.name = "******"
                person.given_name = "******"
                person.surname = "******"
            persons.append(person)
        return persons
