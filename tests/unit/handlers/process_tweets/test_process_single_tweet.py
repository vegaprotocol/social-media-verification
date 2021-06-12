from unittest import mock
from common import SMVConfig

from services.twitter import Tweet
from handlers.process_tweets import process_tweet

twitter_account_name = "twitter_account"
twitter_pubkey = (
    "01152723fa548599255ea0a17cbeb5d92c9659c8d797eb7c1213419218c6b94f"
)
twitter_invalid_signature = "ku39iMD7/SLTxfZUw7SAn5K3mypHGmp7hKpgh0yDIWGRR9Qlc1yqoUOaVbMbgjFU8nNots2BDFKK4f7INVALID=="  # noqa: E501
twitter_signed_message = "ku39iMD7/SLTxfZUw7SAn5K3mypHGmp7hKpgh0yDIWGRR9Qlc1yqoUOaVbMbgjFU8nNots2BDFKK4f79HokbCA=="  # noqa: E501
twitter_tweet_prefix = "I'm taking a ride with @hello_mixel"
twitter_handle = "@hello_mixel"

tweet_ok = Tweet(
    tweet_id=123,
    user_id=321,
    user_screen_name=twitter_account_name,
    full_text=(
        f"I'm taking a ride with @hello_mixel {twitter_pubkey} {twitter_signed_message} "  # noqa: E501
        "https://www.wired.co.uk/article/silicon-roundabout #oldstreettest"
    ),
)

tweet_invalid_format = Tweet(
    tweet_id=123,
    user_id=321,
    user_screen_name=twitter_account_name,
    full_text="Hello!!",
)

tweet_invalid_signature = Tweet(
    tweet_id=123,
    user_id=321,
    user_screen_name=twitter_account_name,
    full_text=(
        f"I'm taking a ride with @hello_mixel {twitter_pubkey} {twitter_invalid_signature} "  # noqa: E501
        "https://www.wired.co.uk/article/silicon-roundabout #oldstreettest"
    ),
)

smv_config = SMVConfig(
    twitter_search_text="I'm taking a ride with",
    twitter_reply_message_success="",
    twitter_reply_message_invalid_format="Tweet has invalid format.",
    twitter_reply_message_invalid_signature="Tweet has invalid signature.",
    twitter_reply_delay=0.1,
)


def test_process_tweet(capsys):
    storage = mock.MagicMock()
    twclient = mock.MagicMock()

    storage.get_tweet_record.return_value = None  # tweet not yet processed

    process_tweet(
        tweet=tweet_ok,
        storage=storage,
        twclient=twclient,
        config=smv_config,
        tweet_prefix=twitter_tweet_prefix,
        twitter_handle=twitter_handle,
    )

    # validate log output
    captured = capsys.readouterr()

    log_line = captured.out.strip()

    assert "\n" not in log_line

    assert '"action":"process_tweet"' in log_line
    assert '"tweet_id":123' in log_line
    assert f'"tweet_handle":"{twitter_account_name}"' in log_line
    assert f'"tweet_message":"{tweet_ok.full_text}"' in log_line
    assert f'"pubkey":"{twitter_pubkey}"' in log_line
    assert f'"signed_message":"{twitter_signed_message}"' in log_line
    assert '"status":"SUCCESS"' in log_line

    # assert DB calls
    assert storage.mock_calls == [
        mock.call.get_tweet_record(123),
        mock.call.upsert_tweet_record(
            tweet_id=tweet_ok.tweet_id,
            user_id=tweet_ok.user_id,
            screen_name=tweet_ok.user_screen_name,
            text=tweet_ok.full_text,
            status="PROCESSING",
        ),
        mock.call.upsert_verified_party(
            twitter_pubkey,
            tweet_ok.user_id,
            tweet_ok.user_screen_name,
        ),
        mock.call.upsert_tweet_record(
            tweet_id=tweet_ok.tweet_id,
            reply="",
            status="PASSED",
        ),
    ]

    # assert twitter API calls
    assert twclient.mock_calls == []


def test_process_tweet_already_processed(capsys):
    storage = mock.MagicMock()
    twclient = mock.MagicMock()

    storage.get_tweet_record.return_value = {}  # tweet already processed

    process_tweet(
        tweet=tweet_ok,
        storage=storage,
        twclient=twclient,
        config=smv_config,
        tweet_prefix=twitter_tweet_prefix,
        twitter_handle=twitter_handle,
    )

    # validate log output
    captured = capsys.readouterr()

    log_line = captured.out.strip()

    assert "\n" not in log_line

    assert '"action":"process_tweet"' in log_line
    assert '"tweet_id":123' in log_line
    assert '"status":"SKIP"' in log_line

    # assert DB calls
    assert storage.mock_calls == [mock.call.get_tweet_record(123)]

    # assert twitter API calls
    assert twclient.mock_calls == []


def test_process_tweet_invalid_format(capsys):
    storage = mock.MagicMock()
    twclient = mock.MagicMock()

    storage.get_tweet_record.return_value = None  # tweet not yet processed

    process_tweet(
        tweet=tweet_invalid_format,
        storage=storage,
        twclient=twclient,
        config=smv_config,
        tweet_prefix=twitter_tweet_prefix,
        twitter_handle=twitter_handle,
    )

    # validate log output
    captured = capsys.readouterr()

    log_line = captured.out.strip()

    assert "\n" not in log_line

    assert '"action":"process_tweet"' in log_line
    assert '"tweet_id":123' in log_line
    assert f'"tweet_handle":"{twitter_account_name}"' in log_line
    assert f'"tweet_message":"{tweet_invalid_format.full_text}"' in log_line
    assert '"error":"Invalid Format"' in log_line
    assert '"status":"FAILED"' in log_line

    # assert DB calls
    assert storage.mock_calls == [
        mock.call.get_tweet_record(123),
        mock.call.upsert_tweet_record(
            tweet_id=tweet_invalid_format.tweet_id,
            user_id=tweet_invalid_format.user_id,
            screen_name=tweet_invalid_format.user_screen_name,
            text=tweet_invalid_format.full_text,
            status="PROCESSING",
        ),
        mock.call.upsert_tweet_record(
            tweet_id=tweet_invalid_format.tweet_id,
            reply="",
            status="INVALID_FORMAT",
        ),
    ]

    # assert twitter API calls
    assert twclient.mock_calls == []


def test_process_tweet_invalid_signature(capsys):
    storage = mock.MagicMock()
    twclient = mock.MagicMock()

    storage.get_tweet_record.return_value = None  # tweet not yet processed

    process_tweet(
        tweet=tweet_invalid_signature,
        storage=storage,
        twclient=twclient,
        config=smv_config,
        tweet_prefix=twitter_tweet_prefix,
        twitter_handle=twitter_handle,
    )

    # validate log output
    captured = capsys.readouterr()

    log_line = captured.out.strip()

    assert "\n" not in log_line

    assert '"action":"process_tweet"' in log_line
    assert '"tweet_id":123' in log_line
    assert f'"tweet_handle":"{twitter_account_name}"' in log_line
    assert f'"tweet_message":"{tweet_invalid_signature.full_text}"' in log_line
    assert f'"pubkey":"{twitter_pubkey}"' in log_line
    assert f'"signed_message":"{twitter_invalid_signature}"' in log_line
    assert '"error":"Invalid Signature"' in log_line
    assert '"status":"FAILED"' in log_line

    # assert DB calls
    assert storage.mock_calls == [
        mock.call.get_tweet_record(123),
        mock.call.upsert_tweet_record(
            tweet_id=tweet_invalid_signature.tweet_id,
            user_id=tweet_invalid_signature.user_id,
            screen_name=tweet_invalid_signature.user_screen_name,
            text=tweet_invalid_signature.full_text,
            status="PROCESSING",
        ),
        mock.call.upsert_tweet_record(
            tweet_id=tweet_invalid_signature.tweet_id,
            reply=smv_config.twitter_reply_message_invalid_signature,
            status="INVALID_SIGNATURE",
        ),
    ]

    # assert twitter API calls
    assert twclient.mock_calls == [
        mock.call.reply(
            smv_config.twitter_reply_message_invalid_signature,
            tweet_invalid_signature,
        )
    ]
