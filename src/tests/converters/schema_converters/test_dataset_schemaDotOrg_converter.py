import datetime

from converters.schema_converters import dataset_converter_schema_dot_org_instance
from database.model.agent.agent_table import AgentTable
from database.model.agent.contact import Contact
from database.model.agent.person import Person
from database.model.ai_asset.license import License
from database.model.ai_resource.alternate_name import AlternateName
from database.model.dataset.dataset import Dataset
from database.model.dataset.size import DatasetSizeORM
from database.model.knowledge_asset.publication import Publication
from database.session import DbSession
from tests.testutils.paths import path_test_resources


def test_aiod_to_schema_dot_org_happy_path(dataset: Dataset):
    dataset.identifier = 1
    dataset.license = License(name="a license")
    dataset.alternate_name = [AlternateName(name="alias1"), AlternateName(name="alias2")]
    dataset.size = DatasetSizeORM(value=1, unit="Rows")
    dataset.keyword = [AlternateName(name="keyword1"), AlternateName(name="keyword2")]
    creator = Contact(name="person name")
    funder = Person(name="Firstname Surname", surname="Surname", firstname="Firstname")
    funder.agent_identifier = AgentTable(identifier="1", type="person")
    dataset.creator = [creator]
    dataset.funder = [funder.agent_identifier]
    dataset.citation = [Publication(name="A Cited Resource", creator=[creator])]
    dataset.aiod_entry.date_modified = datetime.datetime(2023, 8, 22, 1, 2, 3)
    dataset.date_published = datetime.datetime(2023, 8, 22, 4, 5, 6)

    converter = dataset_converter_schema_dot_org_instance
    with DbSession() as session:
        session.add(creator)
        session.add(funder)
        session.commit()
        result = converter.convert(session, dataset)
    actual = result.json(by_alias=True, indent=4)
    with open(path_test_resources() / "schemes" / "schema_dot_org" / "dataset.json", "r") as f:
        expected = f.read()
    for i, (row_actual, row_expected) in enumerate(zip(actual.split("\n"), expected.split("\n"))):
        assert row_actual == row_expected, f"Line {i}: {row_actual} != {row_expected}"
    assert actual == expected
