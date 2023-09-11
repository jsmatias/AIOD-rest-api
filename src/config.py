import pathlib
import tomllib

with open(pathlib.Path(__file__).parent / "config.toml", "rb") as fh:
    CONFIG = tomllib.load(fh)

DB_CONFIG = CONFIG.get("database", {})
KEYCLOAK_CONFIG = CONFIG.get("keycloak", {})
