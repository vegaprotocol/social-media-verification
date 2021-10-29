import pytest
from datetime import datetime, timezone
from tools import setup_parties_collection
from services.smv_storage import SMVStorage

START_TIME = datetime(2021, 9, 13, 20, 12, 55, 1000, timezone.utc)
START_TIME_EPOCH = int(START_TIME.timestamp())

PUB_KEY = "cc3a5912aba19291b070457f54652bb49b1b3a86ef0537e5224dbdc4e83b2102"
TWITTER_ID = 18237215432962
TWITTER_HANDLE = "my_twt_handle"

NEW_PUB_KEY = "7f27932200b4d6d3af14d3896031ffc3b83c2da728b62aa9124905b754cc9c5f"  # noqa: E501
NEW_TWITTER_ID = 54830984309458
NEW_TWITTER_HANDLE = "my_other_twt_handle"


@pytest.mark.skipif_no_mongodb
# fmt: off
@pytest.mark.parametrize(
    "description, new_pub_key,new_twitter_id,new_twitter_handle",
    [
        ("Sing up with same data", PUB_KEY, TWITTER_ID, TWITTER_HANDLE),
        # User changes theirs Pub Key
        ("Update Pub Key", NEW_PUB_KEY, TWITTER_ID, TWITTER_HANDLE),
        # User transfers Pub Key to another Twitter account
        ("Update Twitter ID", PUB_KEY, NEW_TWITTER_ID, TWITTER_HANDLE),
        # User changes their Twitter Handle
        ("Update Twitter Handle", PUB_KEY, TWITTER_ID, NEW_TWITTER_HANDLE),
        # User changes their Pub Key and Twitter Handle - both at once
        ("Update Pub Key and Twitter Handle", NEW_PUB_KEY, TWITTER_ID, NEW_TWITTER_HANDLE),  # noqa: E501
        # User transfers Pub Key to another Twitter account
        ("Update Twitter ID and Twitter Handle", PUB_KEY, NEW_TWITTER_ID, NEW_TWITTER_HANDLE),  # noqa: E501
        # A new participant sign ups with a Twitter Handle, that
        #   belonged (in past) to a different participant
        # We don't want to update data for this use-case, but to create
        #   a new participant and update old one
        # ("Update Pub Key and Twitter ID", NEW_PUB_KEY, NEW_TWITTER_ID, TWITTER_HANDLE),  # noqa: E501
    ],
)
# fmt: on
def test_allowed_user_info_updates(
    smv_storage: SMVStorage,
    new_pub_key: str,
    new_twitter_id: int,
    new_twitter_handle: str,
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
    # Create
    #
    smv_storage.upsert_verified_party(
        pub_key=PUB_KEY,
        user_id=TWITTER_ID,
        screen_name=TWITTER_HANDLE,
    )

    #
    # Update
    #
    smv_storage.upsert_verified_party(
        pub_key=new_pub_key,
        user_id=new_twitter_id,
        screen_name=new_twitter_handle,
    )

    #
    # Validate
    #
    parties = smv_storage.get_parties()
    assert len(parties) == 1
    party = parties[0]
    assert party["twitter_handle"] == new_twitter_handle
    assert party["party_id"] == new_pub_key
    assert party["twitter_user_id"] == new_twitter_id


@pytest.mark.skipif_no_mongodb
# fmt: off
@pytest.mark.parametrize(
    "description, new_pub_key,new_twitter_id,new_twitter_handle",
    [
        ("New user sign ups", NEW_PUB_KEY, NEW_TWITTER_ID, NEW_TWITTER_HANDLE),
        # A new participant sign ups with a Twitter Handle, that
        #   belonged (in past) to a different participant
        # We don't want to update data for this use-case, but to create
        #   a new participant and update old one
        ("Update Pub Key and Twitter ID", NEW_PUB_KEY, NEW_TWITTER_ID, TWITTER_HANDLE),  # noqa: E501
    ],
)
# fmt: on
def test_new_user_sign_ups(
    smv_storage: SMVStorage,
    new_pub_key: str,
    new_twitter_id: int,
    new_twitter_handle: str,
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
    # Create
    #
    smv_storage.upsert_verified_party(
        pub_key=PUB_KEY,
        user_id=TWITTER_ID,
        screen_name=TWITTER_HANDLE,
    )

    #
    # Create another
    #
    smv_storage.upsert_verified_party(
        pub_key=new_pub_key,
        user_id=new_twitter_id,
        screen_name=new_twitter_handle,
    )

    #
    # Validate
    #
    parties = smv_storage.get_parties()
    assert len(parties) == 2
    old_party = parties[0]
    new_party = parties[1]
    assert old_party["twitter_handle"] in TWITTER_HANDLE
    assert old_party["party_id"] == PUB_KEY
    assert old_party["twitter_user_id"] == TWITTER_ID
    assert new_party["twitter_handle"] == new_twitter_handle
    assert new_party["party_id"] == new_pub_key
    assert new_party["twitter_user_id"] == new_twitter_id


@pytest.mark.skipif_no_mongodb
def test_signup_with_twitter_handle_matching_two_participants(
    smv_storage: SMVStorage,
):
    #
    # Prepare
    #
    setup_parties_collection(
        smv_storage,
        [],
    )

    #
    # Create two entries
    #
    smv_storage.upsert_verified_party(
        pub_key=PUB_KEY,
        user_id=TWITTER_ID,
        screen_name=TWITTER_HANDLE,
    )
    smv_storage.upsert_verified_party(
        pub_key=NEW_PUB_KEY,
        user_id=NEW_TWITTER_ID,
        screen_name=NEW_TWITTER_HANDLE,
    )

    #
    # New Sign-up
    #
    smv_storage.upsert_verified_party(
        pub_key=PUB_KEY,
        user_id=TWITTER_ID,
        screen_name=NEW_TWITTER_HANDLE,
    )

    #
    # Validate
    #
    parties = smv_storage.get_parties()
    assert len(parties) == 2
    a_party = parties[0]
    b_party = parties[1]
    assert a_party["party_id"] == PUB_KEY
    assert a_party["twitter_user_id"] == TWITTER_ID
    assert a_party["twitter_handle"] == NEW_TWITTER_HANDLE
    assert b_party["party_id"] == NEW_PUB_KEY
    assert b_party["twitter_user_id"] == NEW_TWITTER_ID
    assert b_party["twitter_handle"] == NEW_TWITTER_HANDLE
