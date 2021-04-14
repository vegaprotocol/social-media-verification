import pytest
from common import TweetInvalidSignatureError
from handlers.process_tweets import validate_signature


@pytest.mark.parametrize(
    "twitter_handle, pubkey, signed_message, comment",
    [
        (
            "twitter_account",
            "01152723fa548599255ea0a17cbeb5d92c9659c8d797eb7c1213419218c6b94f",
            "caq81rZuZ3bHf/IrsDaAkGB2VFdHlydfdCqyChzfh6U+mRi3oeIpXI6WanOIOIva6GZE4i3VgdpX+TWAs/z6CA==",  # noqa: E501
            "signed without @",
        ),
        (
            "twitter_account",
            "01152723fa548599255ea0a17cbeb5d92c9659c8d797eb7c1213419218c6b94f",
            "ku39iMD7/SLTxfZUw7SAn5K3mypHGmp7hKpgh0yDIWGRR9Qlc1yqoUOaVbMbgjFU8nNots2BDFKK4f79HokbCA==",  # noqa: E501
            "signed with @",
        ),
    ],
)
def test_validate_signature(twitter_handle, pubkey, signed_message, comment):
    validate_signature(pubkey, signed_message, twitter_handle)


@pytest.mark.parametrize(
    "twitter_handle, pubkey, signed_message, comment",
    [
        (
            "twitter_account",
            "01152723fa548599255ea0a175d92c9659c8d797eb7c1213419218c6b94f",
            "caq81rZuZ3bHf/IrsDaAkGB2VFdHlydfdCqyChzfh6U+mRi3oeIpXI6WanOIOIva6GZE4i3VgdpX+TWAs/z6CA==",  # noqa: E501
            "malformed pubkey",
        ),
        (
            "twitter_account",
            "01152723fa548599255ea0a17cbeb5d92c9659c8d797eb7c1213419218c6b94f",
            "caq81rZuZ3bHf/IrsDaAkGB2VFdHlydfyChzfh6U+mRi3oeIpXI6WanOIOIva6GZE4i3VgdpX+TWAs/z6CA==",  # noqa: E501
            "malformed signed message",
        ),
        (
            "different_twitter_account",
            "01152723fa548599255ea0a17cbeb5d92c9659c8d797eb7c1213419218c6b94f",
            "caq81rZuZ3bHf/IrsDaAkGB2VFdHlydfdCqyChzfh6U+mRi3oeIpXI6WanOIOIva6GZE4i3VgdpX+TWAs/z6CA==",  # noqa: E501
            "different account name",
        ),
    ],
)
def test_validate_signature_negative(
    twitter_handle, pubkey, signed_message, comment
):
    with pytest.raises(TweetInvalidSignatureError):
        validate_signature(pubkey, signed_message, twitter_handle)
