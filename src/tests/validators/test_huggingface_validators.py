import pytest

from database.validators import huggingface_validators


@pytest.mark.parametrize(
    "identifier,expected_error",
    [
        ("0-hero/OIG-small-chip2", None),
        ("user/Foo-BAR_foo.bar123", None),
        ("acronym_identification", None),
        (
            "user/data/set",
            ValueError(
                "The platform_resource_identifier for HuggingFace should be a valid repo_id. For "
                "new repositories, there should be a single forward slash in the repo_id "
                "(namespace/repo_name). Legacy repositories are without a namespace. This repo_id "
                "has too many forward slashes."
            ),
        ),
        (
            "a",
            ValueError(
                "The platform_resource_identifier for HuggingFace should be a valid repo_id. A "
                "repo_id should be between 1 and 96 characters."
            ),
        ),
        (
            "user/" + "a" * 200,
            ValueError(
                "The platform_resource_identifier for HuggingFace should be a valid repo_id. A "
                "repo_id should be between 1 and 96 characters."
            ),
        ),
    ],
)
def test_identifier(identifier: str, expected_error: ValueError | None):
    if expected_error is None:
        huggingface_validators.throw_error_on_invalid_identifier(identifier)
    else:
        with pytest.raises(type(expected_error)) as exception_info:
            huggingface_validators.throw_error_on_invalid_identifier(identifier)
        assert exception_info.value.args[0] == expected_error.args[0]
