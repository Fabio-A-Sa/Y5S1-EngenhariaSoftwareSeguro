from typing import cast, Literal
import os

def ensure_env(key: str):
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing environment variable {key}")

    return value


def ensure_environment_env():
    value = ensure_env("ENVIRONMENT")
    if value not in ["production", "development"]:
        raise ValueError(
            f'Environment variable ENVIRONMENT must be either "production" or "development", got {value}'
        )

    return cast(Literal["production", "development"], value)


DEVELOPMENT = ensure_environment_env() == "development"
DATA_DIR = ensure_env("DATA_DIR")

# Derived
INSTANCE_DIR = f"{DATA_DIR}/flask_instance"
