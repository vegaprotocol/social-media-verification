import pytest
from freezegun import freeze_time
from datetime import datetime, timezone, timedelta
from tools import setup_parties_collection
from services.smv_storage import SMVStorage

START_TIME = datetime(2021, 9, 13, 10, 34, 20, 1000, timezone.utc)
START_TIME_EPOCH = int(START_TIME.timestamp())

PUB_KEY = "cc3a5912aba19291b070457f54652bb49b1b3a86ef0537e5224dbdc4e83b2102"
TWITTER_ID = 18237215432962
TWITTER_HANDLE = "my_twt_handle"


@pytest.mark.skipif_no_mongodb
def test_insert(smv_storage: SMVStorage):
    setup_parties_collection(
        smv_storage,
        [],
    )

    # Before
    assert smv_storage.get_parties() == []

    # note:
    # - each call to get date-time will tick global time by 15seconds
    # - tz_offset - make sure it works with a random timezone
    with freeze_time(START_TIME, tz_offset=-10, auto_tick_seconds=15):
        # Insert
        smv_storage.upsert_verified_party(
            pub_key=PUB_KEY,
            user_id=TWITTER_ID,
            screen_name=TWITTER_HANDLE,
        )

    # validate
    parties = smv_storage.get_parties()

    assert len(parties) == 1
    party = parties[0]
    assert party["twitter_handle"] == TWITTER_HANDLE
    assert party["party_id"] == PUB_KEY
    assert party["twitter_user_id"] == TWITTER_ID
    assert party["created"] == START_TIME_EPOCH
    assert party["last_modified"] == START_TIME_EPOCH


@pytest.mark.skipif_no_mongodb
def test_dates_after_update(smv_storage: SMVStorage):
    setup_parties_collection(
        smv_storage,
        [],
    )

    #
    # Create
    #

    # note:
    # - each call to get date-time will tick global time by 15seconds
    # - tz_offset - make sure it works with a random timezone
    with freeze_time(START_TIME, tz_offset=-10, auto_tick_seconds=15):
        smv_storage.upsert_verified_party(
            pub_key=PUB_KEY,
            user_id=TWITTER_ID,
            screen_name=TWITTER_HANDLE,
        )
    parties = smv_storage.get_parties()
    assert len(parties) == 1
    party = parties[0]
    assert party["created"] == START_TIME_EPOCH
    assert party["last_modified"] == START_TIME_EPOCH

    #
    # Update
    #

    # note:
    # - each call to get date-time will tick global time by 15seconds
    # - tz_offset - make sure it works with a random timezone
    with freeze_time(
        START_TIME + timedelta(seconds=11), tz_offset=-10, auto_tick_seconds=15
    ):
        smv_storage.upsert_verified_party(
            pub_key=PUB_KEY,
            user_id=TWITTER_ID,
            screen_name=TWITTER_HANDLE,
        )

    parties = smv_storage.get_parties()
    assert len(parties) == 1
    party = parties[0]
    assert party["created"] == START_TIME_EPOCH
    assert party["last_modified"] == START_TIME_EPOCH + 11
