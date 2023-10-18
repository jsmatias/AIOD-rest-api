from typing import Type

from sqlalchemy import DDL, event
from sqlmodel import SQLModel


def create_deletion_trigger_one_to_x(
    trigger: Type[SQLModel],
    trigger_identifier_link: str,
    to_delete: Type[SQLModel],
    to_delete_identifier: str = "identifier",
):
    """
    Create a trigger for a one-to-one or one-to-many relationship, so that if a row from trigger is
    deleted, any row in the to_delete is also deleted where trigger.trigger_identifier_link ==
    to_delete.to_delete_identifier.

    e.g.
    - trigger: Dataset
    - trigger_identifier_link: "ai_asset_identifier"
    - to_delete: AIAssetTable
    - to_delete_identifier: "identifier"
    Then, after deleting a Dataset, the corresponding AIAsset will also be deleted.
    """
    trigger_name = trigger.__tablename__
    delete_name = to_delete.__tablename__

    ddl = DDL(
        f"""
        CREATE TRIGGER delete_{trigger_name}_{delete_name}
        AFTER DELETE ON {trigger_name}
        FOR EACH ROW
        BEGIN
            DELETE FROM {delete_name}
            WHERE {delete_name}.{to_delete_identifier} = OLD.{trigger_identifier_link};
        END;
        """
    )
    event.listen(trigger.metadata, "after_create", ddl)


def create_deletion_trigger_many_to_one(
    trigger: Type[SQLModel],
    to_delete: Type[SQLModel],
    to_delete_identifier: str,
    trigger_identifier_link: str = "identifier",
):
    """
    Create a trigger, so that if trigger is deleted, any orphan row in the to_table is also deleted
    """
    trigger_name = trigger.__tablename__
    delete_name = to_delete.__tablename__

    ddl = DDL(
        f"""
        CREATE TRIGGER delete_{trigger_name}_{delete_name}
        AFTER DELETE ON {trigger_name}
        FOR EACH ROW
        BEGIN
            DELETE FROM {delete_name}
            WHERE {to_delete}.{to_delete_identifier} = OLD.{trigger_identifier_link}
            AND NOT EXISTS (
                SELECT 1 FROM {trigger_name}
                WHERE {trigger_name}.{trigger_identifier_link} = OLD.{trigger_identifier_link}
            );
        END;
        """
    )
    event.listen(trigger.metadata, "after_create", ddl)


def create_deletion_trigger_many_to_many(
    trigger: Type[SQLModel],
    link: Type[SQLModel],
    to_delete: Type[SQLModel],
    trigger_identifier: str = "identifier",
    link_from_identifier: str = "from_identifier",
    link_to_identifier: str = "linked_identifier",
    to_delete_identifier: str = "identifier",
):
    """
    Create a trigger, so that if trigger is deleted, any orphan row in the to_table is also deleted
    """
    trigger_name = trigger.__tablename__
    link_name = link.__tablename__
    delete_name = to_delete.__tablename__

    ddl = DDL(
        f"""
        CREATE TRIGGER delete_{trigger_name}_{delete_name}
        AFTER DELETE ON {trigger_name}
        FOR EACH ROW
        BEGIN
            DELETE FROM {link_name}
            WHERE {link_name}.{link_from_identifier} = OLD.{trigger_identifier}
            DELETE FROM {delete_name}
            WHERE NOT EXISTS (
                SELECT 1 FROM {link_name}
                WHERE {link_name}.{link_to_identifier} = {delete_name}.{to_delete_identifier}
            );
        END;
        """
    )
    event.listen(trigger.metadata, "after_create", ddl)
