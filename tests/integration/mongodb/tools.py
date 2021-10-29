from typing import List
from datetime import datetime, timezone, timedelta
import random
import string

from services.smv_storage import SMVStorage

PARTIES_COLLECTION_NAME = "identities"


def _setup_collection(
    collection_name: str,
    smv_storage: SMVStorage,
    documents: List = None,
):
    smv_storage.db.drop_collection(collection_name)
    parties_col = smv_storage.db.create_collection(collection_name)

    if documents:
        parties_col.insert_many(documents)


def setup_parties_collection(smv_storage: SMVStorage, parties: List = None):
    _setup_collection("identities", smv_storage, parties)


def setup_tweets_collection(smv_storage: SMVStorage, tweets: List = None):
    _setup_collection("tweets", smv_storage, tweets)


def setup_todo_tweets_collection(
    smv_sotrage: SMVStorage,
    tweet_ids: List[int] = None,
):
    _setup_collection(
        "todo_tweets",
        smv_sotrage,
        [{"tweet_id": tid} for tid in tweet_ids],
    )


def random_vega_address() -> str:
    return f"{random.SystemRandom().randrange(16**64):030x}"


def random_string() -> str:
    return "".join(
        random.SystemRandom().choices(
            string.ascii_letters + string.digits,
            k=random.SystemRandom().randrange(5, 20),
        )
    )


def random_text() -> str:
    word_count = random.SystemRandom().randrange(3, 10)
    return " ".join([random_string() for _ in range(word_count)])


NOW = datetime.utcnow().replace(tzinfo=timezone.utc)
OLDEST = NOW - timedelta(days=180)


def random_date(start: datetime = OLDEST, end: datetime = NOW) -> datetime:
    delta_seconds = int((end - start).total_seconds())
    return start + timedelta(
        seconds=random.SystemRandom().randrange(delta_seconds)
    )


def random_party(
    pub_key: str = None,
    created: datetime = None,
    last_modified: datetime = None,
    twitter_handle: str = None,
    twitter_user_id: int = None,
):
    if not pub_key:
        pub_key = random_vega_address()
    if not created:
        created = random_date()
    if not last_modified:
        last_modified = random_date(created)
    if not twitter_handle:
        twitter_handle = random_string()
    if not twitter_user_id:
        twitter_user_id = random.SystemRandom().randint(
            10 ** 5, 9223372036854775807
        )

    return {
        "pub_key": pub_key,
        "created": created,
        "last_modified": last_modified,
        "twitter_handle": twitter_handle,
        "twitter_user_id": twitter_user_id,
    }


def random_tweet(
    tweet_id: int = None,
    user_id: int = None,
    screen_name: str = None,
    text: str = None,
    last_modified: datetime = None,
    reply: str = "",
    status: str = "PASSED",
    description: str = "",
):
    if not tweet_id:
        tweet_id = random.SystemRandom().randint(10 ** 19, 10 ** 20)
    if not screen_name:
        screen_name = random_string()
    if not last_modified:
        last_modified = random_date()
    if not user_id:
        user_id = random.SystemRandom().randint(10 ** 5, 9223372036854775807)
    if not text:
        text = random_text()

    return {
        "tweet_id": tweet_id,
        "user_id": user_id,
        "screen_name": screen_name,
        "text": text,
        "reply": reply,
        "status": status,
        "description": description,
        "last_modified": last_modified,
    }
