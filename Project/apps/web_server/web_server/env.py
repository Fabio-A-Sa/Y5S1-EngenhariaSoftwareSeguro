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

APP_URL = ensure_env("APP_URL")
PUBLIC_AUTHENTICATION_SERVER_URL = ensure_env("PUBLIC_AUTHENTICATION_SERVER_URL")


AUTHENTICATION_SERVER_URL = ensure_env("AUTHENTICATION_SERVER_URL")
AUTHORIZATION_SERVER_URL = ensure_env("AUTHORIZATION_SERVER_URL")
RESOURCE_SERVER_URL = ensure_env("RESOURCE_SERVER_URL")

# Derived
INSTANCE_DIR = f"{DATA_DIR}/flask_instance"
AUTHORIZATION_SERVER_USERS = f"{AUTHORIZATION_SERVER_URL}/api/users"
AUTHORIZATION_SERVER_ROLES = f"{AUTHORIZATION_SERVER_URL}/api/roles"
AUTHORIZATION_SERVER_OPERATIONS = f"{AUTHORIZATION_SERVER_URL}/api/operations"
AUTHORIZATION_SERVER_RESOURCES = f"{AUTHORIZATION_SERVER_URL}/api/resources"


MY_PRIVATE_KEY = ""
AUTHORIZATION_PUBLIC_KEY = ""
RESOURCE_PUBLIC_KEY = ""
