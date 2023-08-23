import pathlib

from connectors.example.example_connector import ExampleConnector
from database.model.agent.organisation import Organisation
from database.model.agent.person import Person
from database.model.dataset.dataset import Dataset
from database.model.knowledge_asset.publication import Publication
from database.model.models_and_experiments.experiment import Experiment
from database.model.models_and_experiments.ml_model import MLModel
from database.model.service.service import Service

_path_example_resources = pathlib.Path(__file__).parent.parent / "example" / "resources"


class ExampleDatasetConnector(ExampleConnector[Dataset]):
    def __init__(self):
        json_path = _path_example_resources / "datasets.json"
        super().__init__(json_path, Dataset)


class ExampleExperimentConnector(ExampleConnector[Experiment]):
    def __init__(self):
        json_path = _path_example_resources / "experiments.json"
        super().__init__(json_path, Experiment)


class ExampleMLModelConnector(ExampleConnector[MLModel]):
    def __init__(self):
        json_path = _path_example_resources / "ml_models.json"
        super().__init__(json_path, MLModel)


class ExampleOrganisationConnector(ExampleConnector[Organisation]):
    def __init__(self):
        json_path = _path_example_resources / "organisations.json"
        super().__init__(json_path, Organisation)


class ExamplePersonConnector(ExampleConnector[Person]):
    def __init__(self):
        json_path = _path_example_resources / "persons.json"
        super().__init__(json_path, Person)


class ExamplePublicationConnector(ExampleConnector[Publication]):
    def __init__(self):
        json_path = _path_example_resources / "publications.json"
        super().__init__(json_path, Publication)


class ExampleServiceConnector(ExampleConnector[Service]):
    def __init__(self):
        json_path = _path_example_resources / "services.json"
        super().__init__(json_path, Service)