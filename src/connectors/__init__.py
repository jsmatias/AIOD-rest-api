import pathlib
from typing import Dict  # noqa:F401

from .abstract.resource_connector import ResourceConnector  # noqa:F401
from .huggingface.huggingface_dataset_connector import HuggingFaceDatasetConnector
from .openml.openml_dataset_connector import OpenMlDatasetConnector
from .zenodo.zenodo_dataset_connector import ZenodoDatasetConnector

dataset_connectors = {
    c.platform_name: c
    for c in (
        OpenMlDatasetConnector(),
        HuggingFaceDatasetConnector(),
        ZenodoDatasetConnector(),
    )
}

_path_example_resources = pathlib.Path(__file__).parent / "example" / "resources"

example_connectors = {
    # "datasets": ExampleDatasetConnector(),
    # "educational_resources": ExampleConnector(
    #     resource_class=EducationalResource,
    #     json_path=_path_example_resources / "educational_resources.json",
    # ),
    # "news": ExampleConnector(resource_class=News,
    # json_path=_path_example_resources / "news.json"),
    # "events": ExampleConnector(
    #     resource_class=Event, json_path=_path_example_resources / "events.json"
    # ),
    # "presentations": ExampleConnector(
    #     resource_class=Presentation, json_path=_path_example_resources / "presentations.json"
    # ),
    # "projects": ExampleConnector(
    #     resource_class=Project, json_path=_path_example_resources / "projects.json"
    # ),
    # "publications": ExampleConnector(
    #     resource_class=PublicationOld, json_path=_path_example_resources / "publications.json"
    # ),
    # # "organisations": ExampleConnector(
    # #     resource_class=OrganisationOld, json_path=_path_example_resources / "organisations.json"
    # # ),
}  # type: Dict[str, ResourceConnector]
