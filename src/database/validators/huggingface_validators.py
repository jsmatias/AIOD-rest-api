import re

REPO_ID_ILLEGAL_CHARACTERS = re.compile(r"[^0-9a-zA-Z-_./]+")
MSG_PREFIX = "The platform_resource_identifier for HuggingFace should be a valid repo_id. "


def throw_error_on_invalid_identifier(platform_resource_identifier: str):
    """
    Throw a ValueError on an invalid repository identifier.

    Valid repo_ids:
        Between 1 and 96 characters.
        Either “repo_name” or “namespace/repo_name”
        [a-zA-Z0-9] or ”-”, ”_”, ”.”
        ”—” and ”..” are forbidden

    Refer to:
    https://huggingface.co/docs/huggingface_hub/package_reference/utilities#huggingface_hub.utils.validate_repo_id
    """
    repo_id = platform_resource_identifier
    if REPO_ID_ILLEGAL_CHARACTERS.search(repo_id):
        msg = "A repo_id should only contain [a-zA-Z0-9] or ”-”, ”_”, ”.”"
        raise ValueError(MSG_PREFIX + msg)
    if not (1 < len(repo_id) < 96):
        msg = "A repo_id should be between 1 and 96 characters."
        raise ValueError(MSG_PREFIX + msg)
    if repo_id.count("/") > 1:
        msg = (
            "For new repositories, there should be a single forward slash in the repo_id ("
            "namespace/repo_name). Legacy repositories are without a namespace. This repo_id has "
            "too many forward slashes."
        )
        raise ValueError(MSG_PREFIX + msg)
    if ".." in repo_id:
        msg = "A repo_id may not contain multiple consecutive dots."
        raise ValueError(MSG_PREFIX + msg)
