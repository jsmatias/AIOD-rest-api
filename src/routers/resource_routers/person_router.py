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
    def _verify_user_roles(person, user: User | None):
        if (person.platform == "drupal") and not (
            user and user.has_role("full_view_drupal_resources")
        ):
            person.name = "******"
            person.given_name = "******"
            person.surname = "******"
        return person

    def _retrieve_resource(self, session, identifier, user=None, platform=None):
        person = super()._retrieve_resource(session, identifier, platform)
        return self._verify_user_roles(person, user)

    def _retrieve_resources(self, session, pagination, user=None, platform=None):
        persons = super()._retrieve_resources(session, pagination, user, platform)
        persons = [self._verify_user_roles(person, user) for person in persons]
        return persons
