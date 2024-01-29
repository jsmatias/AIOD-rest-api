import pytest

from database.validators import zenodo_validators

ERROR_MSG = (
    "The platform_resource_identifier for Zenodo should be "
    "a valid repository identifier or a valid file identifier. "
    "A repository identifier has the following pattern: "
    "the string 'zenodo.org:' followed by an integer: e.g., zenodo.org:100. \n"
    "A file identifier is a string composed by a group of 8 characters, "
    "3 groups of 4 characters, and a group of 12 characters, where the characters "
    "include letters and numbers and the groups are separated by a dash '-': "
    "e.g, abcde123-abcd-0000-ab00-abcdef000000."
)


@pytest.mark.parametrize(
    "repo_id,expected_error",
    [
        ("zenodo.org:1", None),
        ("zenodo.org:1234567", None),
        ("zenodo.org:02334", ValueError(ERROR_MSG)),
        ("zenodo_org:100", ValueError(ERROR_MSG)),
        ("zenodo.org.100", ValueError(ERROR_MSG)),
        ("zenodo.org.abc", ValueError(ERROR_MSG)),
        ("11111111-9999-0000-1111-123456789012", None),
        ("abcdefgh-abcd-abcd-abcd-abcdefghijkl", None),
        ("abcde123-abcd-0000-ab00-abcdef000000", None),
        ("ABCde123-abcd-0000-ab00-abcdef000000", ValueError(ERROR_MSG)),
        ("abdef123_abcd-0000-ab00-abcdef000000", ValueError(ERROR_MSG)),
        ("abd.0123-abcd-0000-ab00-abcdef000000", ValueError(ERROR_MSG)),
        ("abdef-23-abcd-0000-ab00-abcdef000000", ValueError(ERROR_MSG)),
        ("abcd0123-abcd-0000-ab00-abcdef0000000", ValueError(ERROR_MSG)),
        ("abcd0123-abcd0-0000-ab00-abcdef000000", ValueError(ERROR_MSG)),
        ("abcd0123-abcd-00000-ab00-abcdef000000", ValueError(ERROR_MSG)),
        ("abcd0123-abcd-0000-ab000-abcdef000000", ValueError(ERROR_MSG)),
    ],
)
def test_repo_id(repo_id: str, expected_error: ValueError | None):
    if expected_error is None:
        zenodo_validators.throw_error_on_invalid_identifier(repo_id)

    else:
        with pytest.raises(type(expected_error)) as exception_info:
            zenodo_validators.throw_error_on_invalid_identifier(repo_id)
        assert exception_info.value.args[0] == expected_error.args[0]
