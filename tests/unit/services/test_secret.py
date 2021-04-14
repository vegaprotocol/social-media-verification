from unittest import mock
import os

from services.secret import (
    get_json_secret_from_env,
    get_json_secret_from_gcp,
)


@mock.patch.dict(os.environ, {"SECRET": '{"USER": "user1", "PORT": 9001}'})
def test_get_json_secret_from_env():
    assert get_json_secret_from_env(env_var_name="SECRET") == {
        "USER": "user1",
        "PORT": 9001,
    }


@mock.patch("google.cloud.secretmanager.SecretManagerServiceClient")
def test_get_secret_from_gcp(SecretManagerServiceClientMock):
    # a mocked instance of SecretManagerServiceClient
    secret_service = mock.MagicMock()
    SecretManagerServiceClientMock.return_value = secret_service

    # SecretManagerServiceClient.access_secret_version(name="SECRET NAME")
    payload_response = mock.MagicMock()
    payload_response.payload.data = b'{"USER": "user1", "PORT": 9001}'
    secret_service.access_secret_version.return_value = payload_response

    # execute
    assert get_json_secret_from_gcp(secret_name="SECRET") == {
        "USER": "user1",
        "PORT": 9001,
    }

    # validate `access_secret_version` was called once with a specific argument
    secret_service.access_secret_version.assert_called_once_with(name="SECRET")
