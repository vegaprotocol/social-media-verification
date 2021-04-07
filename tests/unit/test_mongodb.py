import pytest
from unittest import mock
import os

from smv.helpers.mongodb import get_mongodb_connection

MONGODB_DATA = {
    "DB_USER": "user1",
    "DB_PASS": "pa55w0rd",
    "DB_HOSTNAME": "awesome.mongo.com",
    "DB_NAME": "smv",
}
STR_MONGO_DATA = """
{
    "DB_USER": "user2",
    "DB_PASS": "pa55w0rD",
    "DB_HOSTNAME": "Awesome.mongo",
    "DB_NAME": "smv-db"
}
"""


@mock.patch.dict(
    os.environ,
    {"MONGO_SECRET_NAME": "projects/123456/secrets/db-secret/versions/last"},
)
@mock.patch("pymongo.MongoClient")
@mock.patch(
    "smv.helpers.mongodb.get_json_secret_from_gcp",
    return_value=MONGODB_DATA,
)
def test_get_mongodb_connection_env_var_with_gcp_secret_name(
    get_json_secret_from_gcp_mock: mock.MagicMock,
    MongoClientMock: mock.MagicMock,
):
    mongo_client = mock.MagicMock()
    connection = mock.MagicMock()
    MongoClientMock.return_value = mongo_client
    mongo_client.get_database.return_value = connection

    assert (
        get_mongodb_connection(gcp_secret_name="MONGO_SECRET_NAME")
        == connection
    )
    get_json_secret_from_gcp_mock.assert_called_once_with(
        "projects/123456/secrets/db-secret/versions/last"
    )
    MongoClientMock.assert_called_once_with(
        "mongodb+srv://user1:pa55w0rd@awesome.mongo.com/smv?"
        "retryWrites=true&w=majority"
    )
    mongo_client.get_database.assert_called_once_with("smv")


@mock.patch("pymongo.MongoClient")
@mock.patch(
    "smv.helpers.mongodb.get_json_secret_from_gcp",
    return_value=MONGODB_DATA,
)
def test_get_mongodb_connection_no_env(
    get_json_secret_from_gcp_mock: mock.MagicMock,
    MongoClientMock: mock.MagicMock,
):
    mongo_client = mock.MagicMock()
    connection = mock.MagicMock()
    MongoClientMock.return_value = mongo_client
    mongo_client.get_database.return_value = connection

    assert (
        get_mongodb_connection(
            gcp_secret_name="projects/123456/secrets/db-secret/versions/last"
        )
        == connection
    )
    get_json_secret_from_gcp_mock.assert_called_once_with(
        "projects/123456/secrets/db-secret/versions/last"
    )
    MongoClientMock.assert_called_once_with(
        "mongodb+srv://user1:pa55w0rd@awesome.mongo.com/smv?"
        "retryWrites=true&w=majority"
    )
    mongo_client.get_database.assert_called_once_with("smv")


@mock.patch.dict(os.environ, {"MONGO_SECRET": STR_MONGO_DATA})
@mock.patch("pymongo.MongoClient")
def test_get_mongodb_connection_env_var_with_secret(
    MongoClientMock: mock.MagicMock,
):
    mongo_client = mock.MagicMock()
    connection = mock.MagicMock()
    MongoClientMock.return_value = mongo_client
    mongo_client.get_database.return_value = connection

    assert get_mongodb_connection(gcp_secret_name="MONGO_SECRET") == connection
    MongoClientMock.assert_called_once_with(
        "mongodb+srv://user2:pa55w0rD@Awesome.mongo/smv-db?"
        "retryWrites=true&w=majority"
    )
    mongo_client.get_database.assert_called_once_with("smv-db")


def test_get_mongodb_connection_negative():
    with pytest.raises(ValueError):
        get_mongodb_connection(gcp_secret_name="UNKNOWN_ENV_VAR")
