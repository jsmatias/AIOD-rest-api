import logging
from importlib.metadata import version

format_string = (
    f"v{version('aiod_metadata_catalogue')}"
    + " %(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s"
)


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
