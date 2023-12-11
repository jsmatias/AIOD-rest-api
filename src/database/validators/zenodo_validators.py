import re

MSG_PREFIX = "The platform_resource_identifier for Zenodo should be a valid repo_id. "


def throw_error_on_invalid_identifier(platform_resource_identifier: str):
    """
    Throw a ValueError on an invalid repository identifier.

    Valid repo_id:
        zenodo.org:<int>
    """
    repo_id = platform_resource_identifier
    pattern = re.compile(r"^zenodo.org:[1-9][0-9]*$")
    if not pattern.match(repo_id):
        msg = "A repo_id has the following pattern: "
        "the string 'zenodo.org:' followed by an integer."
        "E.g., zenodo.org:100"
        raise ValueError(MSG_PREFIX + msg)
