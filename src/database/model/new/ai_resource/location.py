from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from database.model.new.ai_resource.country import Country
from database.model.new.field_length import NORMAL, SHORT
from database.model.relationships import ResourceRelationshipSingle
from serialization import AttributeSerializer, FindByNameDeserializer


# TODO(jos) --> this is not tested yet


class LocationBase(SQLModel):
    pass


class LocationORM(LocationBase, table=True):  # type: ignore [call-arg]
    __tablename__ = "location"

    identifier: int | None = Field(primary_key=True)
    address_identifier: int | None = Field(foreign_key="address.identifier")
    address: Optional["AddressORM"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
    geo_identifier: int | None = Field(foreign_key="geo.identifier")
    geo: Optional["GeoORM"] = Relationship(sa_relationship_kwargs={"cascade": "all, delete"})


class Location(LocationBase):
    """A physical location"""

    address: Optional["Address"] = Field(default=None)
    geo: Optional["Geo"] = Field(default=None)


class GeoBase(SQLModel):
    latitude: float | None = Field(
        default=None,
        description="The latitude of a location in " "degrees (WGS84)",
        schema_extra={"example": 37.42242},
    )
    longitude: float | None = Field(
        default=None,
        description="The longitude of a location in " "degrees (WGS84)",
        schema_extra={"example": -122.08585},
    )
    elevation_millimeters: int | None = Field(
        default=None,
        description="The elevation in millimeters with " "tespect to the WGS84 ellipsoid",
    )


class GeoORM(GeoBase, table=True):  # type: ignore [call-arg]
    __tablename__ = "geo"
    identifier: int | None = Field(primary_key=True)


class Geo(GeoBase):
    """The geographic coordinates of a physical location"""

    address: Optional["Address"] = Field(default=None)


class AddressBase(SQLModel):
    region: str | None = Field(
        description="A subdivision of the country. Not necessary for most " "countries. ",
        max_length=NORMAL,
        default=None,
        schema_extra={"example": "California"},
    )
    locality: str | None = Field(
        description="A city, town or village.",
        max_length=NORMAL,
        default=None,
        schema_extra={"example": "Paris"},
    )
    street: str | None = Field(
        description="The street address.",
        default=None,
        max_length=NORMAL,
        schema_extra={"example": "Wetstraat 170"},
    )
    postal_code: str | None = Field(
        description="The postal code.",
        default=None,
        max_length=SHORT,
        schema_extra={"example": "1040 AA"},
    )
    address: str | None = Field(
        description="Free text, in case the separate parts such as the "
        "street, postal code and country cannot be confidently "
        "separated.",
        default=None,
        max_length=NORMAL,
        schema_extra={"example": "Wetstraat 170, 1040 Brussel"},
    )


class AddressORM(AddressBase, table=True):  # type: ignore [call-arg]
    __tablename__ = "address"

    identifier: int | None = Field(primary_key=True)

    country_identifier: int | None = Field(foreign_key="license.identifier")
    country: Optional[Country] = Relationship(
        back_populates="address", sa_relationship_kwargs={"cascade": "all, delete"}
    )

    class RelationshipConfig:
        country: Optional[str] = ResourceRelationshipSingle(
            identifier_name="country_identifier",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(Country),
        )


class Address(AddressBase):
    """A postal address"""

    country: Country = Field(
        default=None,
        description="The country as ISO 3166-1 alpha-3",
        max_length=3,
        min_length=3,
        schema_extra={"example": "BEL"},
    )
