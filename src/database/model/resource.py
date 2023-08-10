from typing import Type, Tuple

from pydantic import create_model
from sqlalchemy import CheckConstraint
from sqlalchemy.util import classproperty
from sqlmodel import SQLModel, Field, UniqueConstraint
from sqlmodel.main import FieldInfo

from database.model.new.helper_functions import get_relationships, all_annotations
from database.model.relationships import ResourceRelationshipInfo
from serialization import create_getter_dict
from database.model.platform.platform_names import PlatformName


class Resource(SQLModel):
    """Every top-level class in our API, meaning every class that can be directly accessed
    through a route, should inherit from `Resource`."""

    platform: str | None = Field(
        default=None,
        description="The external platform on which this item can be "
        "found. Leave empty if this item originates from "
        "AIoD. If platform is not None, "
        "the platform_identifier should be set as well.",
        schema_extra={"example": PlatformName.zenodo},
        foreign_key="platform.name",
    )
    platform_identifier: str | None = Field(
        description="A unique identifier issued by the external platform that's specified in "
        "'platform'. Leave empty if this item is not part of an external platform.",
        default=None,
        schema_extra={"example": "1"},
    )

    @classproperty
    def __table_args__(cls) -> Tuple:
        return (
            UniqueConstraint(
                "platform",
                "platform_identifier",
                name="same_platform_and_platform_identifier",
            ),
            CheckConstraint(
                "(platform IS NULL) <> (platform_identifier IS NOT NULL)",
                name=f"{cls.__name__}_platform_xnor_platform_id_null",
            ),
        )


def _get_field_definitions(
    resource_class: Type[Resource],
    relationships: dict[str, ResourceRelationshipInfo],
    filter_create: bool = False,
) -> dict[str, Tuple[Type, FieldInfo]]:
    if not hasattr(resource_class, "RelationshipConfig"):
        return {}
    return {
        attribute_name: (
            all_annotations(resource_class.RelationshipConfig)[attribute_name],  # the type
            relationshipConfig.field(),  # The Field()
        )
        for attribute_name, relationshipConfig in relationships.items()
        if not filter_create or relationshipConfig.include_in_create
    }


def resource_create(resource_class: Type[Resource]) -> Type[SQLModel]:
    """
    Create a SQLModel for a Create class of a resource. This Create class is a Pydantic class
    that can be used for POST and PUT requests (and thus has no identifier), and is not backed by a
    ORM table.

    Besides the default attributes, this class has the Pydantic-version of the relationships. If the
    resource has a relationship to an "enum table", for instance, this will just be a string value
    in this Create class.

    See https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/ for background.
    """
    relationships = get_relationships(resource_class)
    field_definitions = _get_field_definitions(resource_class, relationships, filter_create=True)

    model = create_model(
        resource_class.__name__ + "Create", __base__=resource_class.__base__, **field_definitions
    )
    return model


def resource_read(resource_class: Type[Resource]) -> Type[SQLModel]:
    """
    Create a SQLModel for a Read class of a resource. This Read class is a Pydantic class
    that can be used for GET requests (and thus has a required identifier), and is not backed by a
    ORM table.

    Besides the default attributes, this class has the Pydantic-version of the relationships. If the
    resource has a relationship to an "enum table", for instance, this will just be a string value
    in this Read class.

    See https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/ for background.
    """
    relationships = get_relationships(resource_class)
    field_definitions = _get_field_definitions(resource_class, relationships)
    field_definitions.update({"identifier": (int, Field())})
    resource_class_read = create_model(
        resource_class.__name__ + "Read", __base__=resource_class.__base__, **field_definitions
    )
    _update_model_serialization(resource_class, resource_class_read)
    relationships.items()
    return resource_class_read


def _update_model_serialization(resource_class: Type[SQLModel], resource_class_read):
    """
    For every Serializer defined on the RelationshipConfig of the resource, use this Serializer in
    a newly created GetterDict (this is Pydantic functionality) and put in on the config of this
    resource.
    """
    relationships = get_relationships(resource_class)
    if hasattr(resource_class, "RelationshipConfig"):
        getter_dict = create_getter_dict(
            {
                attribute_name: relationshipConfig.serializer
                for attribute_name, relationshipConfig in relationships.items()
                if relationshipConfig.serializer is not None
            }
        )
        resource_class_read.__config__.getter_dict = getter_dict
