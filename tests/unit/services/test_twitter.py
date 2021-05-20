from unittest import mock
import os
from services.twitter import Tweet, TwitterClient


def test_tweet_constructor():
    assert Tweet(123, 321, "user", "tweet message")


TWITTER_SECRET_DATA = {
    "ACCOUNT_NAME": "user1",
    "CONSUMER_KEY": "pa55w0rd",
    "CONSUMER_SECRET": "5ecret",
    "ACCESS_TOKEN": "accessT",
    "ACCESS_SECRET": "a5ecrettt",
}


@mock.patch.dict(
    os.environ,
    {"TWITTER_SECRET_NAME": "projects/12/secrets/twt-secret/versions/last"},
)
@mock.patch("services.twitter.Twython")
@mock.patch(
    "services.twitter.get_json_secret_from_gcp",
    return_value=TWITTER_SECRET_DATA,
)
def test_twitter_client_constructor(
    get_json_secret_from_gcp_mock: mock.MagicMock,
    TwythonMock: mock.MagicMock,
):
    tw_auth = mock.MagicMock()
    TwythonMock.return_value = tw_auth
    tw_auth.obtain_access_token.return_value = "abc"
    assert TwitterClient(gcp_secret_name="TWITTER_SECRET_NAME")

    get_json_secret_from_gcp_mock.assert_called_once_with(
        "projects/12/secrets/twt-secret/versions/last"
    )

    assert TwythonMock.mock_calls == [
        mock.call("pa55w0rd", "5ecret", "accessT", "a5ecrettt"),
    ]


tweet_1 = {
    "id": 1381726215963168769,
    "full_text": "test tweet",
    "user": {
        "id": 24324324242432,
        "screen_name": "test_user",
    },
}


def test_search():
    twclient = mock.MagicMock()
    twclient.twapi.search.side_effect = [
        {
            "statuses": [tweet_1],
            "search_metadata": {"next_results": "something"},
        },
        {
            "statuses": [tweet_1],
            "search_metadata": {"next_results": "something"},
        },
        {"statuses": [tweet_1], "search_metadata": {}},
    ]

    result = list(TwitterClient.search(twclient, "search"))

    assert len(result) == 3

    assert twclient.mock_calls == [
        mock.call.twapi.search(
            q="search",
            count=100,
            include_entities=True,
            tweet_mode="extended",
        ),
        mock.call.twapi.search(
            q="search",
            count=100,
            include_entities=True,
            tweet_mode="extended",
            max_id=1381726215963168768,
        ),
        mock.call.twapi.search(
            q="search",
            count=100,
            include_entities=True,
            tweet_mode="extended",
            max_id=1381726215963168768,
        ),
    ]


def test_mentions():
    twclient = mock.MagicMock()
    twclient.twapi.get_mentions_timeline.side_effect = [
        [tweet_1],
        [],
    ]
    since_id = 123

    result = list(TwitterClient.mentions(twclient, since_id))

    assert len(result) == 1

    assert twclient.mock_calls == [
        mock.call.twapi.get_mentions_timeline(
            count=100,
            include_entities=True,
            tweet_mode="extended",
            since_id=since_id,
        ),
        mock.call.twapi.get_mentions_timeline(
            count=100,
            include_entities=True,
            tweet_mode="extended",
            since_id=since_id,
            max_id=tweet_1["id"] - 1,
        ),
    ]
