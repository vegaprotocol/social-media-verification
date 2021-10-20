import pytest
from datetime import datetime, timezone
from tools import setup_parties_collection
from services.smv_storage import SMVStorage
from common import BlocklistPartyError

START_TIME = datetime(2021, 9, 13, 20, 12, 55, 1000, timezone.utc)
START_TIME_EPOCH = int(START_TIME.timestamp())

A_PUB_KEY = "cc3a5912aba19291b070457f54652bb49b1b3a86ef0537e5224dbdc4e83b2102"
A_TWITTER_ID = 18237215432962
A_TWITTER_HANDLE = "twitter_handle_a"

B_PUB_KEY = "7f27932200b4d6d3af14d3896031ffc3b83c2da728b62aa9124905b754cc9c5f"
B_TWITTER_ID = 54830984309458
B_TWITTER_HANDLE = "twitter_handle_b"

C_PUB_KEY = "acfc8c549698b74010bcd2965a76d410c6c74c04151eef1b03d8bcd79fd01aa2"
C_TWITTER_ID = 4934572934
C_TWITTER_HANDLE = "twitter_handle_c"


@pytest.mark.skipif_no_mongodb
# fmt: off
@pytest.mark.parametrize(
    "description, pub_key,twitter_id,twitter_handle",
    [
        ("Transfer address from A to B v1", A_PUB_KEY, B_TWITTER_ID, B_TWITTER_HANDLE),
        ("Transfer address from A to B v2", A_PUB_KEY, B_TWITTER_ID, A_TWITTER_HANDLE),
        ("Transfer address from A to B v3 - ignore twitter handle match with another party",
            A_PUB_KEY, B_TWITTER_ID, C_TWITTER_HANDLE),
        ("Transfer address from B to A v1", B_PUB_KEY, A_TWITTER_ID, A_TWITTER_HANDLE),
        ("Transfer address from B to A v2", B_PUB_KEY, A_TWITTER_ID, B_TWITTER_HANDLE),
        ("Transfer address from B to A v3 - ignore twitter handle match with another party",
            B_PUB_KEY, A_TWITTER_ID, C_TWITTER_HANDLE),
    ],
)
# fmt: on
def test_block_participants(
    smv_storage: SMVStorage,
    pub_key: str,
    twitter_id: int,
    twitter_handle: str,
    description: str,
):
    #
    # Prepare
    #
    setup_parties_collection(
        smv_storage,
        [],
    )

    #
    # Create three entries
    #
    smv_storage.upsert_verified_party(
        pub_key=A_PUB_KEY,
        user_id=A_TWITTER_ID,
        screen_name=A_TWITTER_HANDLE,
    )
    smv_storage.upsert_verified_party(
        pub_key=B_PUB_KEY,
        user_id=B_TWITTER_ID,
        screen_name=B_TWITTER_HANDLE,
    )
    smv_storage.upsert_verified_party(
        pub_key=C_PUB_KEY,
        user_id=C_TWITTER_ID,
        screen_name=C_TWITTER_HANDLE,
    )

    #
    # New Sign-up
    #
    with pytest.raises(BlocklistPartyError):
        smv_storage.upsert_verified_party(
            pub_key=pub_key,
            user_id=twitter_id,
            screen_name=twitter_handle,
        )

    #
    # Validate
    #
    parties = smv_storage.get_parties()
    assert len(parties) == 1, "Parties A and B should be blocked and not returned by get_parties"
    party = parties[0]
    assert party["twitter_handle"] == C_TWITTER_HANDLE
    assert party["party_id"] == C_PUB_KEY
    assert party["twitter_user_id"] == C_TWITTER_ID
