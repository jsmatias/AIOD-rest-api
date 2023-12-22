import re

REPO_ID_PATTERN = r"^zenodo\.org:[1-9][0-9]*$"
FILE_ID_PATTERN = r"^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$"
PATTERN = re.compile("|".join([REPO_ID_PATTERN, FILE_ID_PATTERN]))


def throw_error_on_invalid_identifier(platform_resource_identifier: str):
    """
    Throw a ValueError on an invalid repository or distribution identifier.

    Valid repository identifier is the string 'zenodo.org:' followed by an integer::
        zenodo.org:<int>

    Valid distribution identifier is a string composed by a group of 8 characters,
    3 groups of 4 characters, and a group of 12 characters, where the characters
    include letters and numbers and the groups are separated by a dash '-' as the
    following example:
        abcde123-abcd-0000-ab00-abcdef000000
    """
    repo_id = platform_resource_identifier
    if not PATTERN.match(repo_id):
        msg = (
            "The platform_resource_identifier for Zenodo should be "
            "a valid repository identifier or a valid file identifier. "
            "A repository identifier has the following pattern: "
            "the string 'zenodo.org:' followed by an integer: e.g., zenodo.org:100. \n"
            "A file identifier is a string composed by a group of 8 characters, "
            "3 groups of 4 characters, and a group of 12 characters, where the characters "
            "include letters and numbers and the groups are separated by a dash '-': "
            "e.g, abcde123-abcd-0000-ab00-abcdef000000."
        )
        raise ValueError(msg)
