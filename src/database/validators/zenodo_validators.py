import re

MSG_PREFIX = "The platform_resource_identifier for Zenodo should be "
"a valid repository identifier or a valid file identifier. "

repo_id_pattern = r"(?:\Azenodo.org:[1-9]\d*\Z)"
file_id_pattern = r"(?:\A[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}\Z)"
pattern = re.compile("|".join([repo_id_pattern, file_id_pattern]))


def throw_error_on_invalid_identifier(platform_resource_identifier: str):
    """
    Throw a ValueError on an invalid repository or distribution identifier.

    Valid repository identifier:
        zenodo.org:<int>
    Valid distribution identifier:

    """
    repo_id = platform_resource_identifier
    if not pattern.match(repo_id):
        msg = "A repository identifier has the following pattern: "
        "the string 'zenodo.org:' followed by an integer: e.g., zenodo.org:100. \n"
        "A file identifier is a string composed by a group of 8 characters, "
        "3 groups of 4 characters, and a group of 12 characters, where the characters "
        "include letters and numbers and the groups are separated by a dash '-': "
        "e.g, abcde123-abcd-0000-ab00-abcdef000000."
        raise ValueError(MSG_PREFIX + msg)
