from unittest import mock
import flask
import re
from handlers.parties import handle_parties


def test_handle_parties(capsys):
    collection = mock.MagicMock()
    db = mock.MagicMock()
    db.get_collection.return_value = collection
    collection.find.return_value = [
        {"pub_key": "pub key 1", "twitter_handle": "handle 1"},
        {"pub_key": "pub key 2", "twitter_handle": "handle 2"},
    ]

    app = flask.Flask("test")

    # execute
    with app.test_request_context():
        response = handle_parties(db)  # type: flask.Response

    # validate response
    assert response.status_code == 200
    assert response.json == [
        {"party_id": "pub key 1", "twitter_handle": "handle 1"},
        {"party_id": "pub key 2", "twitter_handle": "handle 2"},
    ]

    # validate function calls
    assert db.mock_calls == [
        mock.call.get_collection("identities"),
        mock.call.get_collection().find(),
    ]

    # validate log
    captured = capsys.readouterr()

    assert re.match(
        r'^{"time":"[^"]*","action":"handle_parties",'
        r'"parties_count":2,"time_ms":0,"status":"SUCCESS"}$',
        captured.out,
    )
