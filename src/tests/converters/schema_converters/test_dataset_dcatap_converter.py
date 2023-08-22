import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session

from converters.schema_converters import dataset_converter_dcatap_instance
from database.model.dataset.dataset import Dataset
from tests.testutils.paths import path_test_resources


@pytest.mark.skip(reason="TODO")
def test_aiod_to_dcatap_happy_path(engine: Engine, dataset: Dataset):
    converter = dataset_converter_dcatap_instance
    with Session(engine) as session:
        dcat_ap = converter.convert(session, dataset)
    actual = dcat_ap.json(by_alias=True, indent=4)
    with open(path_test_resources() / "schemes" / "dcatap" / "dataset.json", "r") as f:
        expected = f.read()
    for i, (row_actual, row_expected) in enumerate(zip(actual.split("\n"), expected.split("\n"))):
        assert row_actual == row_expected, f"Line {i}: {row_actual} != {row_expected}"
    assert actual == expected
