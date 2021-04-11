# -*- coding: utf-8 -*-
from typing import Optional
import json
import os


def get_json_secret_from_gcp(secret_name: Optional[str] = None) -> dict:
    """Retrives secret from Google Cloud Platform: Secret Manager,
    and deserialize it from json to python object.

    Args:
        secret_name (str): A secret name in GCP Secret Manager.

    Returns:
        A deserialized json secret from GCP Secret Manager

    Raises:
        json.JSONDecodeError: If the secret value is not valid json.

    """
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(name=secret_name)
    payload = response.payload.data.decode("UTF-8")

    return json.loads(payload)


def get_json_secret_from_env(*, env_var_name: str) -> dict:
    """Retrives secret from Environment variable,
    and deserialize it from json to python object.

    Args:
        env_var_name (str): Environment variable containing secret value.

    Returns:
        A deserialized json object from Environment Variable

    Raises:
        ValueError: If environment variable from `env_var_name` is not set.
        json.JSONDecodeError: If the secret value is not valid json.

    """
    payload = os.getenv(env_var_name)
    if payload is None:
        raise ValueError(
            "Failed to get secret from environment variable: "
            f'environment variable "{env_var_name}" is not set.'
        )
    return json.loads(payload)
