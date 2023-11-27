import dataclasses
from typing import TypeVar, Generic, List

from sqlmodel import SQLModel

from database.model.concept.concept import AIoDConcept
from database.model.annotations import datatype_of_field

RESOURCE = TypeVar("RESOURCE", bound=SQLModel)


@dataclasses.dataclass
class ResourceWithRelations(Generic[RESOURCE]):
    """
    A resource, with related AIResources in a dictionary of {field_name: other resource(s)}.
    """

    resource: RESOURCE
    resource_ORM_class: type[SQLModel]
    related_resources: dict[str, AIoDConcept | List[AIoDConcept]] = dataclasses.field(
        default_factory=dict
    )
    # For each field name, another resource or a list of other resources

    def __post_init__(self):
        for name, value in self.related_resources.items():
            """
            Field type check to avoid mismatch.
            type(value[0]) returns class - <class 'pydantic.main.PublicationCreate'>,
            however datatype_of_field returns str ex - 'Publication'

            """
            name_type = datatype_of_field(clazz=self.resource_ORM_class, field_name=name)
            if type(name_type) is not str:
                name_type = name_type.__name__

            for v in value:
                if name_type + "Create" != type(v).__name__:
                    raise ValueError(
                        f"""Type mismatch for field '{name}'.
                        Expected {name_type}, got {type(v).__name__}."""
                    )
