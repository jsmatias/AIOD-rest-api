from typing import Type, TypeVar

from converters.schema.schema_dot_org import (
    SchemaDotOrgDataset,
    SchemaDotOrgOrganization,
    SchemaDotOrgPerson,
    SchemaDotOrgDataDownload,
)
from converters.schema_converters.schema_converter import SchemaConverter
from database.model.dataset.dataset import Dataset


class DatasetConverterSchemaDotOrg(SchemaConverter[Dataset, SchemaDotOrgDataset]):
    """
    Convert an AIoD Dataset into a schema.org json-ld representation.
    """

    @property
    def to_class(self) -> Type[SchemaDotOrgDataset]:
        return SchemaDotOrgDataset

    def convert(self, aiod: Dataset) -> SchemaDotOrgDataset:
        temporal_coverage_parts = [
            d.isoformat()
            for d in [aiod.temporal_coverage_from, aiod.temporal_coverage_to]
            if d is not None
        ]
        temporal_coverage = (
            "/".join(temporal_coverage_parts) if len(temporal_coverage_parts) > 0 else None
        )
        return SchemaDotOrgDataset(
            description=aiod.description,
            identifier=aiod.identifier,
            name=aiod.name,
            maintainer=SchemaDotOrgOrganization(name=aiod.platform),
            alternateName=_list_to_one_or_none([a.name for a in aiod.alternate_names]),
            # citation=_list_to_one_or_none(aiod.citations),
            creator=SchemaDotOrgPerson(name=aiod.creator) if aiod.creator is not None else None,
            dateModified=aiod.date_modified,
            datePublished=aiod.date_published,
            isAccessibleForFree=aiod.is_accessible_for_free,
            keywords=_list_to_one_or_none([a.name for a in aiod.keywords]),
            sameAs=aiod.same_as,
            version=aiod.version,
            url=f"https://aiod.eu/api/datasets/{aiod.identifier}",  # TODO: update url
            distribution=_list_to_one_or_none(
                [
                    SchemaDotOrgDataDownload(
                        name=d.name,
                        description=d.description,
                        contentUrl=d.content_url,
                        contentSize=d.content_size_kb,
                        encodingFormat=d.encoding_format,
                    )
                    for d in aiod.distributions
                ]
            ),
            funder=SchemaDotOrgPerson(name=aiod.funder) if aiod.funder is not None else None,
            hasPart=_list_to_one_or_none(aiod.has_parts),
            isPartOf=_list_to_one_or_none(aiod.is_part),
            issn=aiod.issn,
            license=aiod.license.name if aiod.license is not None else None,
            measurementTechnique=_list_to_one_or_none([m.technique for m in aiod.measured_values]),
            size=str(aiod.size) if aiod.size is not None else None,
            spatialCoverage=aiod.spatial_coverage,
            temporalCoverage=temporal_coverage,
            variableMeasured=_list_to_one_or_none([m.variable for m in aiod.measured_values]),
        )


V = TypeVar("V")


def _list_to_one_or_none(value: set[V] | list[V]) -> set[V] | list[V] | V | None:
    """All schema.org fields can be repeated. This function can be used to return None if the
    input is empty, return the only value if there is only one value, or otherwise return the
    input set/list.
    """
    if len(value) == 0:
        return None
    if len(value) == 1:
        (only,) = value
        return only
    return value
