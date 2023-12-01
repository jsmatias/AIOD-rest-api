import copy
from unittest.mock import Mock

import huggingface_hub
import pytest
import responses
from starlette import status
from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model.dataset.dataset import Dataset
from database.session import DbSession
from tests.testutils.paths import path_test_resources
from uploader.hugging_face_uploader import _throw_error_on_invalid_repo_id


def test_happy_path_new_repository(
    client: TestClient, mocked_privileged_token: Mock, dataset: Dataset
):
    dataset = copy.deepcopy(dataset)
    dataset.platform = "huggingface"
    dataset.platform_resource_identifier = "Fake-username/test"

    keycloak_openid.userinfo = mocked_privileged_token
    with DbSession() as session:
        session.add(dataset)
        session.commit()

    with open(path_test_resources() / "uploaders" / "huggingface" / "example.csv", "rb") as f:
        files = {"file": f.read()}

    with responses.RequestsMock() as mocked_requests:
        mocked_requests.add(
            responses.POST,
            "https://huggingface.co/api/repos/create",
            json={"url": "url"},
            status=200,
        )
        huggingface_hub.upload_file = Mock(return_value=None)
        response = client.post(
            "/upload/datasets/1/huggingface",
            params={"username": "Fake-username", "token": "Fake-token"},
            headers={"Authorization": "Fake token"},
            files=files,
        )

    assert response.status_code == 200, response.json()
    id_response = response.json()
    assert id_response == 1


def test_repo_already_exists(client: TestClient, mocked_privileged_token: Mock, dataset: Dataset):
    keycloak_openid.userinfo = mocked_privileged_token

    dataset = copy.deepcopy(dataset)
    dataset.platform = "huggingface"
    dataset.platform_resource_identifier = "Fake-username/test"

    with DbSession() as session:
        session.add(dataset)
        session.commit()

    with open(path_test_resources() / "uploaders" / "huggingface" / "example.csv", "rb") as f:
        files = {"file": f.read()}

    with responses.RequestsMock() as mocked_requests:
        mocked_requests.add(
            responses.POST,
            "https://huggingface.co/api/repos/create",
            json={
                "error": "You already created this dataset repo",
                "url": "url",
            },
            status=409,
        )
        huggingface_hub.upload_file = Mock(return_value=None)
        response = client.post(
            "/upload/datasets/1/huggingface",
            params={"username": "Fake-username", "token": "Fake-token"},
            headers={"Authorization": "Fake token"},
            files=files,
        )
    assert response.status_code == 200, response.json()
    id_response = response.json()
    assert id_response == 1


def test_wrong_platform(client: TestClient, mocked_privileged_token: Mock, dataset: Dataset):
    keycloak_openid.userinfo = mocked_privileged_token

    dataset = copy.deepcopy(dataset)
    dataset.platform = "example"
    dataset.platform_resource_identifier = "Fake-username/test"

    with DbSession() as session:
        session.add(dataset)
        session.commit()

    with open(path_test_resources() / "uploaders" / "huggingface" / "example.csv", "rb") as f:
        files = {"file": f.read()}

    response = client.post(
        "/upload/datasets/1/huggingface",
        params={"username": "Fake-username", "token": "Fake-token"},
        headers={"Authorization": "Fake token"},
        files=files,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert (
        response.json()["detail"]
        == "The dataset with identifier 1 should have platform=PlatformName.huggingface."
    )


@pytest.mark.parametrize(
    "username,dataset_name,expected_error",
    [
        ("0-hero", "0-hero/OIG-small-chip2", None),
        ("user", "user/Foo-BAR_foo.bar123", None),
        (
            "user",
            "user/Test name with ?",
            ValueError(
                "The platform_resource_identifier for HuggingFace should be a valid repo_id. "
                "A repo_id should only contain [a-zA-Z0-9] or ”-”, ”_”, ”.”"
            ),
        ),
        (
            "username",
            "acronym_identification",
            ValueError(
                "The username should be part of the platform_resource_identifier for HuggingFace: "
                "username/acronym_identification. Please update the dataset "
                "platform_resource_identifier."
            ),
        ),
        (
            "user",
            "user/data/set",
            ValueError(
                "The platform_resource_identifier for HuggingFace should be a valid repo_id. "
                "For new repositories, there should be a single forward slash in the repo_id "
                "(namespace/repo_name). Legacy repositories are without a namespace. This "
                "repo_id has too many forward slashes."
            ),
        ),
        (
            "user",
            "wrong-namespace/name",
            ValueError(
                "The namespace should be equal to the username, but wrong-namespace != user."
            ),
        ),
        (
            "user",
            "user/" + "a" * 200,
            ValueError(
                "The platform_resource_identifier for HuggingFace should be a valid repo_id. "
                "A repo_id should be between 1 and 96 characters."
            ),
        ),
    ],
)
def test_repo_id(username: str, dataset_name: str, expected_error: ValueError | None):
    if expected_error is None:
        _throw_error_on_invalid_repo_id(username, dataset_name)
    else:
        with pytest.raises(type(expected_error)) as exception_info:
            _throw_error_on_invalid_repo_id(username, dataset_name)
        assert exception_info.value.args[0] == expected_error.args[0]
