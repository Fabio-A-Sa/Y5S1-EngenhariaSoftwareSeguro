import os
import pathlib


def ensure_env(key: str):
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing environment variable {key}")

    return value


def abs_path(path_str: str):
    path = pathlib.Path(path_str)
    return str(path.absolute())


DATA_DIR = abs_path(ensure_env("DATA_DIR"))
TOKEN_KEY = ensure_env("TOKEN_KEY")

# Derived
INSTANCE_DIR = f"{DATA_DIR}/flask_instance"
