import pytest
from common import TweetInvalidFormatError
from handlers.process_tweets import parse_tweet_message


#
# Different format messages
#
@pytest.mark.parametrize(
    "twitter_handle",
    [
        "@twitter_account",
    ],
)
@pytest.mark.parametrize(
    "pubkey",
    [
        "6308f99aa2d2a34cb55da860d4cc7127c23ee7036832f947f4a69d30afb6797e",
    ],
)
@pytest.mark.parametrize(
    "msg_sign",
    [
        "BqWxgF8o+qKolb/NdnRPtF5eHQyyOa2laUul6DyAEfEKCOC33UZk3wGfv6QCtYnFDuAPNVnZNst9emz3DgYxCw==",  # noqa: E501
    ],
)
@pytest.mark.parametrize(
    "message",
    [
        "{twitter_handle} {pubkey} {msg_sign}",
        "{pubkey} {msg_sign} {twitter_handle}",
        "{pubkey} {twitter_handle} {msg_sign}",
        "I'm taking a ride on {twitter_handle}\n{pubkey} {msg_sign}\nhttps://test.url #something",  # noqa: E501
        "Join me!! I'm taking a ride on {twitter_handle} 🔥 {pubkey} {msg_sign}\nhttps://test.url",  # noqa: E501
        "Join me!! I'm taking a ride on {twitter_handle}\t{msg_sign} abc {pubkey} :hello!",  # noqa: E501
    ],
)
def test_parse_tweet_message(
    twitter_handle: str, pubkey: str, msg_sign: str, message: str
):
    message = (
        message.replace("{twitter_handle}", twitter_handle)
        .replace("{pubkey}", pubkey)
        .replace("{msg_sign}", msg_sign)
    )
    # regular test
    assert parse_tweet_message(message, twitter_handle) == (
        pubkey,
        msg_sign,
    )


twitter_handle = "@twitter_account"
pubkey = "6308f99aa2d2a34cb55da860d4cc7127c23ee7036832f947f4a69d30afb6797e"
msg_sign = "BqWxgF8o+qKolb/NdnRPtF5eHQyyOa2laUul6DyAEfEKCOC33UZk3wGfv6QCtYnFDuAPNVnZNst9emz3DgYxCw=="  # noqa: E501


#
# Malformed Message
#
@pytest.mark.parametrize(
    "message",
    [
        f"I'm taking a ride on @another_acc {pubkey} {msg_sign}",
        f"I'm taking a ride on {twitter_handle} {pubkey}",
        f"I'm taking a ride on {twitter_handle} {msg_sign}",
    ],
)
def test_parse_message_invalid_format(message):
    with pytest.raises(TweetInvalidFormatError):
        parse_tweet_message(message, twitter_handle)
