from typing import Any, Optional
from pymongo import database
from pymongo.collection import Collection
from datetime import datetime, timezone
from .mongodb import get_mongodb_connection


class SMVStorage(object):
    """Access SMV Storage (currently backed with MongoDB)"""

    def __init__(self, db: database.Database) -> None:
        self.db = db

    @classmethod
    def get_storage(cls, *, gcp_secret_name: str) -> "SMVStorage":
        return SMVStorage(
            get_mongodb_connection(gcp_secret_name=gcp_secret_name)
        )

    @property
    def col_identities(self) -> Collection:
        return self.db.get_collection("identities")

    @property
    def col_tweets(self) -> Collection:
        return self.db.get_collection("tweets")

    def get_parties(self):
        return [
            {
                "party_id": item["pub_key"],
                "twitter_handle": item["twitter_handle"],
                "twitter_user_id": item["twitter_user_id"],
            }
            for item in self.col_identities.find()
        ]

    def upsert_verified_party(
        self,
        pub_key: str,
        user_id: int,
        screen_name: str,
    ):
        self.col_identities.update_one(
            {"pub_key": pub_key},
            {
                "$set": {
                    "twitter_user_id": user_id,
                    "twitter_handle": screen_name,
                    "last_modified": datetime.utcnow().replace(
                        tzinfo=timezone.utc
                    ),
                }
            },
            upsert=True,
        )

    def get_tweet_record(self, tweet_id: int) -> Optional[Any]:
        return self.col_tweets.find_one({"tweet_id": tweet_id})

    def upsert_tweet_record(
        self,
        tweet_id: int,
        user_id: int = None,
        screen_name: str = None,
        text: str = None,
        reply: str = None,
        status: str = None,
    ):
        data = {
            "last_modified": datetime.utcnow().replace(tzinfo=timezone.utc),
        }
        if user_id is not None:
            data["user_id"] = user_id
        if screen_name is not None:
            data["screen_name"] = screen_name
        if text is not None:
            data["text"] = text
        if reply is not None:
            data["reply"] = reply
        if status is not None:
            data["status"] = status
        self.col_tweets.update_one(
            {"tweet_id": tweet_id},
            {"$set": data},
            upsert=True,
        )
