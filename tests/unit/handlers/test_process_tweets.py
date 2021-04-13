import pytest
from common import TweetInvalidFormatError
from handlers.process_tweets import parse_message


#
# Different format messages
#
@pytest.mark.parametrize(
    "message, prefix, expected_pubkey, expected_signed_message",
    [
        (
            (
                "I'm taking a ride with @tweeter_acc "
                "6308f99aa2d2a34cb55da860d4cc7127c23ee7036832f947f4a69d30afb6797e "  # noqa: E501
                "BqWxgF8o+qKolb/NdnRPtF5eHQyyOa2laUul6DyAEfEKCOC33UZk3wGfv6QCtYnFDuAPNVnZNst9emz3DgYxCw== "  # noqa: E501
                "https://www.wired.co.uk/article/silicon-roundabout #oldstreettest"  # noqa: E501
            ),
            "I'm taking a ride with @tweeter_acc",
            "6308f99aa2d2a34cb55da860d4cc7127c23ee7036832f947f4a69d30afb6797e",
            "BqWxgF8o+qKolb/NdnRPtF5eHQyyOa2laUul6DyAEfEKCOC33UZk3wGfv6QCtYnFDuAPNVnZNst9emz3DgYxCw==",  # noqa: E501
        ),
    ],
)
def test_parse_message(
    message, prefix, expected_pubkey, expected_signed_message
):
    # regular test
    assert parse_message(message, prefix) == (
        expected_pubkey,
        expected_signed_message,
    )


#
# Different whitespaces
#
@pytest.mark.parametrize(
    "whitechar",
    [
        "\n",
        "\t",
        "\r",
        " ",
        "    ",
        "\n\t",
    ],
)
def test_parse_message_whitechar(whitechar):
    prefix = "I'm taking a ride with @tweeter_acc"
    pubkey = "6308f99aa2d2a34cb55da860d4cc7127c23ee7036832f947f4a69d30afb6797e"
    signed_message = "BqWxgF8o+qKolb/NdnRPtF5eHQyyOa2laUul6DyAEfEKCOC33UZk3wGfv6QCtYnFDuAPNVnZNst9emz3DgYxCw=="  # noqa: E501
    suffix = (
        "https://www.wired.co.uk/article/silicon-roundabout #oldstreettest"
    )

    message = f"{prefix}{whitechar}{pubkey}{whitechar}{signed_message}{whitechar}{suffix}"  # noqa: E501

    assert parse_message(message, prefix) == (pubkey, signed_message)


#
# Malformed Message
#
@pytest.mark.parametrize(
    "message, prefix",
    [
        (
            (
                "I'm taking a ride with @twitter_acc "
                "6308f99aa2d2a34cb55da860d4cc7127c23ee7036832f947f4a69d30afb6797e "  # noqa: E501
                "BqWxgF8o+qKolb/NdnRPtF5eHQyyOa2laUul6DyAEfEKCOC33UZk3wGfv6QCtYnFDuAPNVnZNst9emz3DgYxCw== "  # noqa: E501
                "https://www.wired.co.uk/article/silicon-roundabout #oldstreettest"  # noqa: E501
            ),
            "I'm taking a ride with @someone_else",
        ),
        ("", "I'm taking a ride with @twitter_acc"),
        (
            "I'm taking a ride with @twitter_acc 6308f99aa2d2a34cb55da860d4cc7127c23ee7036832f947f4a69d30afb6797e",  # noqa: E501
            "I'm taking a ride with @twitter_acc",
        ),
    ],
)
def test_parse_message_invalid_format(message, prefix):
    with pytest.raises(TweetInvalidFormatError):
        parse_message(message, prefix)
