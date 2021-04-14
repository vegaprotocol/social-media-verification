from unittest import mock
from services.smv_storage import SMVStorage


def test_constructor():
    db = mock.MagicMock()
    assert SMVStorage(db)


@mock.patch(
    "services.smv_storage.get_mongodb_connection",
    return_value=mock.MagicMock(),
)
def test_get_storage(
    get_mongodb_connection_mock: mock.MagicMock,
):

    storage = SMVStorage.get_storage(gcp_secret_name="TEST_DB_SECRET")

    assert storage
    assert isinstance(storage, SMVStorage)
    get_mongodb_connection_mock.assert_called_once_with(
        gcp_secret_name="TEST_DB_SECRET"
    )


def test_properties():
    db = mock.MagicMock()
    SMVStorage(db).col_identities
    assert db.mock_calls == [
        mock.call.get_collection("identities"),
    ]
    db = mock.MagicMock()
    SMVStorage(db).col_tweets
    assert db.mock_calls == [
        mock.call.get_collection("tweets"),
    ]


def test_upsert_tweet_record():
    db = mock.MagicMock()
    storage = SMVStorage(db)

    storage.upsert_tweet_record(
        tweet_id=123, user_id="user.1", text="Test tweet", status="OK"
    )
    assert db.mock_calls == [
        mock.call.get_collection("tweets"),
        mock.call.get_collection().update_one(
            {"tweet_id": 123},
            {
                "$set": {
                    "user_id": "user.1",
                    "text": "Test tweet",
                    "status": "OK",
                    "last_modified": mock.ANY,
                }
            },
            upsert=True,
        ),
    ]
