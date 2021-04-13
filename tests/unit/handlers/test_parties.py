from unittest import mock
import flask
import re
from handlers.parties import handle_parties


def test_handle_parties(capsys):
    store = mock.MagicMock()
    store.get_parties.return_value = [
        {"party_id": "pub key 1", "twitter_handle": "handle 1"},
        {"party_id": "pub key 2", "twitter_handle": "handle 2"},
    ]

    app = flask.Flask("test")

    # execute
    with app.test_request_context():
        response = handle_parties(store)  # type: flask.Response

    # validate response
    assert response.status_code == 200
    assert response.json == [
        {"party_id": "pub key 1", "twitter_handle": "handle 1"},
        {"party_id": "pub key 2", "twitter_handle": "handle 2"},
    ]

    # validate function calls
    assert store.mock_calls == [
        mock.call.get_parties(),
    ]

    # validate log
    captured = capsys.readouterr()

    assert re.match(
        r'^{"time":"[^"]*","action":"handle_parties",'
        r'"parties_count":2,"time_ms":0,"status":"SUCCESS"}$',
        captured.out,
    )
