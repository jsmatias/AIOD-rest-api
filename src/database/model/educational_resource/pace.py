from database.model.named_relation import NamedRelation


class Pace(NamedRelation, table=True):  # type: ignore [call-arg]
    __tablename__ = "educational_resource_pace"
