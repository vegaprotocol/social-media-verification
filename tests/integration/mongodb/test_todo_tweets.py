from typing import List
import pytest
from tools import (
    setup_todo_tweets_collection,
    setup_tweets_collection,
    random_tweet,
)
from services.smv_storage import SMVStorage

@pytest.mark.skipif_no_mongodb
def test_get_limit_results(smv_storage: SMVStorage):
    setup_todo_tweets_collection(
        smv_storage,
        list(range(300)),
    )

    assert len(smv_storage.get_todo_tweets()) == 50

@pytest.mark.skipif_no_mongodb
def test_get_remove_duplicates(smv_storage: SMVStorage):
    setup_todo_tweets_collection(
        smv_storage,
        list(range(1,10)) + list(range(12,20)) + list(range(5,15)),
    )

    assert sorted(smv_storage.get_todo_tweets()) == list(range(1,20))


@pytest.mark.skipif_no_mongodb
@pytest.mark.parametrize(
    "tweet_ids",
    [
        [4985058204853905830],
        [12, 32, 190],
        [12, 32, 190, 904932, 123213, 343243, 13213, 42432, 2434],
    ],
)
def test_add_todo_tweets(smv_storage: SMVStorage, tweet_ids: List[int]):
    setup_todo_tweets_collection(
        smv_storage,
        [],
    )

    # Before
    assert smv_storage.get_todo_tweets() == []

    # Insert
    for tweet_id in tweet_ids:
        smv_storage.add_todo_tweet(tweet_id)

    # Verify
    assert sorted(tweet_ids) == sorted(smv_storage.get_todo_tweets())


@pytest.mark.skipif_no_mongodb
@pytest.mark.parametrize(
    "todo_tweet_ids,tweet_ids,todo_after_cleanup",
    [
        ([1,2,3], [], [1,2,3]),
        ([1,2,3], [2], [1,3]),
        ([1,2,3], [2,3,4,5], [1]),
        ([], [2,3,4,5], []),
        ([2,3], [2,3,4,5], []),
    ],
)
def test_cleanup(
    smv_storage: SMVStorage,
    todo_tweet_ids: List[int],
    tweet_ids: List[int],
    todo_after_cleanup: List[int],
):
    setup_todo_tweets_collection(
        smv_storage,
        todo_tweet_ids,
    )
    setup_tweets_collection(
        smv_storage,
        [random_tweet(tweet_id) for tweet_id in tweet_ids],
    )

    # Before
    assert sorted(smv_storage.get_todo_tweets()) == sorted(todo_tweet_ids)

    # Cleanup
    smv_storage.cleanup_todo_tweets()

    # Validate after
    assert sorted(smv_storage.get_todo_tweets()) == sorted(todo_after_cleanup)
