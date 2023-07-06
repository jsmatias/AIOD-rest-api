import pathlib
from typing import Dict  # noqa:F401

from database.model.case_study.case_study import CaseStudy
from database.model.computational_resource.computational_resource import ComputationalResource
from database.model.educational_resource.educational_resource import EducationalResource
from database.model.event.event import Event
from database.model.news.news import News
from database.model.presentation.presentation import Presentation
from database.model.project.project import Project
from database.model.publication.publication import Publication
from database.model.organisation.organisation import Organisation
from .abstract.resource_connector_by_date import ResourceConnectorByDate  # noqa:F401
from .example.example_connector import ExampleConnector
from .example.example_dataset_connector import ExampleDatasetConnector

"""
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
"""

_path_example_resources = pathlib.Path(__file__).parent / "example" / "resources"

example_connectors = {
    "case_studies": ExampleConnector(
        resource_class=CaseStudy, json_path=_path_example_resources / "case_studies.json"
    ),
    "computational_resources": ExampleConnector(
        resource_class=ComputationalResource,
        json_path=_path_example_resources / "computational_resources.json",
    ),
    "datasets": ExampleDatasetConnector(),
    "educational_resources": ExampleConnector(
        resource_class=EducationalResource,
        json_path=_path_example_resources / "educational_resources.json",
    ),
    "news": ExampleConnector(resource_class=News, json_path=_path_example_resources / "news.json"),
    "events": ExampleConnector(
        resource_class=Event, json_path=_path_example_resources / "events.json"
    ),
    "presentations": ExampleConnector(
        resource_class=Presentation, json_path=_path_example_resources / "presentations.json"
    ),
    "projects": ExampleConnector(
        resource_class=Project, json_path=_path_example_resources / "projects.json"
    ),
    "publications": ExampleConnector(
        resource_class=Publication, json_path=_path_example_resources / "publications.json"
    ),
    "organisations": ExampleConnector(
        resource_class=Organisation, json_path=_path_example_resources / "organisations.json"
    ),
}  # type: Dict[str, ResourceConnectorByDate]
