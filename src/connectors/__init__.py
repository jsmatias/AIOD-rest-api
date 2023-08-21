import pathlib
from typing import Dict  # noqa:F401

from database.model.agent.organisation import Organisation
from database.model.agent.person import Person
from database.model.dataset.dataset import Dataset
from database.model.knowledge_asset.publication import Publication
from database.model.models_and_experiments.experiment import Experiment
from database.model.models_and_experiments.ml_model import MLModel
from database.model.service.service import Service
from .example.example_connector import ExampleConnector

_path_example_resources = pathlib.Path(__file__).parent / "example" / "resources"

example_connectors = {
    name: ExampleConnector(
        resource_class=cls,
        json_path=_path_example_resources / f"{name}.json",
    )
    for name, cls in (
        ("datasets", Dataset),
        ("experiments", Experiment),
        ("ml_models", MLModel),
        ("organisations", Organisation),
        ("persons", Person),
        ("publications", Publication),
        ("services", Service),
    )
}  # type: Dict[str, ExampleConnector]
