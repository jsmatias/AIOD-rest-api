from sqlalchemy import Column, Integer, ForeignKey
from sqlmodel import Field

from database.model.new.concept.concept import AIoDConceptBase


class DistributionBase(AIoDConceptBase):
    content_url: str = Field(
        max_length=250,
        schema_extra={"example": "https://www.example.com/dataset/file.csv"},
    )
    content_size_kb: int | None = Field(schema_extra={"example": 10000})
    description: str | None = Field(
        max_length=5000, schema_extra={"example": "Description of this file."}
    )
    encoding_format: str | None = Field(max_length=255, schema_extra={"example": "text/csv"})
    name: str | None = Field(max_length=150, schema_extra={"example": "Name of this file."})


def distribution_for_table(table_name: str):
    class DistributionORM(DistributionBase, table=True):  # type: ignore [call-arg]
        __tablename__ = "distribution_" + table_name

        identifier: int | None = Field(primary_key=True)

        asset_identifier: int | None = Field(
            sa_column=Column(Integer, ForeignKey(table_name + ".identifier", ondelete="CASCADE"))
        )
        # checksum: List[ChecksumORM] = Relationship(
        #     back_populates="distribution", sa_relationship_kwargs={"cascade": "all, delete"}
        # )

        # class RelationshipConfig:
        #     checksum: List[Checksum] = ResourceRelationshipList(
        #         deserializer=CastDeserializer(ChecksumORM)
        #     )

    # Renaming the class. This is not necessary, but useful for debuggin
    DistributionORM.__name__ = DistributionORM.__qualname__ = "DistributionORM" + table_name
    return DistributionORM


class Distribution(DistributionBase):
    """All or part of an AIAsset in downloadable form"""

    pass
    # checksum: List["Checksum"] = Field(default_factory=list)
