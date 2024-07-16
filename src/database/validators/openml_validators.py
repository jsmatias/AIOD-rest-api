MSG = "An OpenML platform_resource_identifier should be a positive integer."


def throw_error_on_invalid_identifier(platform_resource_identifier: str):
    """Throw a ValueError on an invalid repository identifier."""
    try:
        openml_identifier = int(platform_resource_identifier)
    except ValueError:
        raise ValueError(MSG)
    if openml_identifier < 0:
        raise ValueError(MSG)
