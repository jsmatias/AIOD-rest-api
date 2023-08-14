from database.model.named_relation import NamedRelation


class LicenseOld(NamedRelation, table=True):  # type: ignore [call-arg]
    """
    A license document, indicated by URL.
    """

    __tablename__ = "license_old"
