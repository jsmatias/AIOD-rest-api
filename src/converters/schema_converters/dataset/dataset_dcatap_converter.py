import re
from typing import Type

from converters.schema.dcat import (
    DcatApWrapper,
    DcatAPDataset,
    VCardIndividual,
    DcatAPIdentifier,
    DcatAPDistribution,
    SpdxChecksum,
    DcatLocation,
    DcatAPObject,
    XSDDateTime,
    DctPeriodOfTime,
)
from converters.schema_converters.schema_converter import SchemaConverter
from database.model.dataset.dataset import Dataset


class DatasetConverterDcatAP(SchemaConverter[Dataset, DcatApWrapper]):
    """
    Convert an AIoD Dataset into a dcat-ap json-ld representation.
    """

    @property
    def to_class(self) -> Type[DcatApWrapper]:
        return DcatApWrapper

    def convert(self, aiod: Dataset) -> DcatApWrapper:
        release_date = (
            XSDDateTime(value_=aiod.date_published) if aiod.date_published is not None else None
        )
        update_date = (
            XSDDateTime(value_=aiod.date_modified) if aiod.date_modified is not None else None
        )
        dataset = DcatAPDataset(
            id_=aiod.identifier,
            description=aiod.description,
            title=aiod.name,
            keyword=[k.name for k in aiod.keywords],
            landing_page=[aiod.same_as] if aiod.same_as is not None else [],
            theme=[measured_value.variable for measured_value in aiod.measured_values],
            release_date=release_date,
            update_date=update_date,
            version=aiod.version,
        )
        graph: list[DcatAPObject] = [dataset]
        if aiod.contact is not None and len(aiod.contact) > 0:
            contact = VCardIndividual(
                id_=_replace_special_chars("individual_{}".format(aiod.contact)), fn=aiod.contact
            )
            graph.append(contact)
            dataset.contact_point = [DcatAPIdentifier(id_=contact.id_)]
        if aiod.creator is not None and len(aiod.creator) > 0:
            creator = VCardIndividual(
                id_=_replace_special_chars("individual_{}".format(aiod.creator)), fn=aiod.creator
            )
            if creator.id_ not in {obj.id_ for obj in graph}:
                graph.append(creator)
            dataset.creator = [DcatAPIdentifier(id_=creator.id_)]
        if aiod.publisher is not None and len(aiod.publisher) > 0:
            publisher = VCardIndividual(
                id_=_replace_special_chars("individual_{}".format(aiod.publisher)),
                fn=aiod.publisher,
            )
            if publisher.id_ not in {obj.id_ for obj in graph}:
                graph.append(publisher)
            dataset.contact_point = [DcatAPIdentifier(id_=publisher.id_)]
        if aiod.spatial_coverage is not None:
            location = DcatLocation(id_=aiod.spatial_coverage, geometry=aiod.spatial_coverage)
            dataset.spatial_coverage = [DcatAPIdentifier(id_=location.id_)]
            graph.append(location)
        from_, to_ = aiod.temporal_coverage_from, aiod.temporal_coverage_to
        if from_ is not None or to_ is not None:
            from_str = from_.isoformat() if from_ else "-"
            to_str = to_.isoformat() if to_ else "-"
            period = DctPeriodOfTime(id_=f"period_{from_str}_to_{to_str}")
            if from_:
                period.start_date = XSDDateTime(value_=from_)
            if to_ is not None:
                period.end_date = XSDDateTime(value_=to_)
            graph.append(period)
            dataset.temporal_coverage = [DcatAPIdentifier(id_=period.id_)]
        for aiod_distribution in aiod.distributions:
            checksum: SpdxChecksum | None = None
            if len(aiod_distribution.checksum) > 0:
                aiod_checksum = aiod_distribution.checksum[0]
                checksum = SpdxChecksum(
                    id_=aiod_checksum.value,
                    algorithm=aiod_checksum.algorithm.name
                    if aiod_checksum.algorithm is not None
                    else None,
                    checksumValue=aiod_checksum.value,
                )
                graph.append(checksum)
            distribution = DcatAPDistribution(
                id_=aiod_distribution.content_url,
                title=aiod_distribution.name,
                access_url=aiod_distribution.content_url,
                checksum=DcatAPIdentifier(id_=checksum.id_) if checksum is not None else None,
                download_url=aiod_distribution.content_url,
                description=aiod_distribution.description,
                format=aiod_distribution.encoding_format,
                license=aiod.license.name if aiod.license is not None else None,
            )
            dataset.distribution.append(DcatAPIdentifier(id_=aiod_distribution.content_url))
            graph.append(distribution)
        return DcatApWrapper(graph_=graph)


def _replace_special_chars(name: str) -> str:
    """Replace special characters with underscores.

    Args:
        name: a name of a json-ld object.

    Returns:
        a sanitized version of the name
    """
    return re.sub("[^A-Za-z0-9]", "_", name)
