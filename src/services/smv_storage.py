from typing import Any, Optional, Dict
import pymongo
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
                "last_modified": int(
                    item["last_modified"]
                    .replace(tzinfo=timezone.utc)
                    .timestamp()
                ),
                # created might be missing in DB - use "last_modified" then
                # TODO: remove usage of "last_modified" once no longer neede
                "created": int(
                    item.get("created", item["last_modified"])
                    .replace(tzinfo=timezone.utc)
                    .timestamp()
                ),
            }
            for item in self.col_identities.find()
        ]

    def upsert_verified_party(
        self,
        pub_key: str,
        user_id: int,
        screen_name: str,
    ):
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.col_identities.update_one(
            {"pub_key": pub_key},
            {
                "$set": {
                    "twitter_user_id": user_id,
                    "twitter_handle": screen_name,
                    "last_modified": now,
                },
                # `created` field is modified on document INSERT only.
                # It is not modified on document UPDATE.
                "$setOnInsert": {
                    "created": now,
                },
            },
            # UPSERT !!
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

    def get_tweet_count_by_status(self) -> Dict[str, int]:
        return {
            s["_id"]: s["count"]
            for s in self.col_tweets.aggregate(
                [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                    {"$sort": {"_id": pymongo.DESCENDING}},
                ]
            )
        }

    def get_last_tweet_id(self) -> Optional[int]:
        last_tweet = self.col_tweets.find_one(
            projection={"tweet_id": 1, "_id": False},
            sort=[("tweet_id", pymongo.DESCENDING)],
        )
        if last_tweet:
            return last_tweet["tweet_id"]
        return None

    def get_tweet_count(self) -> int:
        return self.col_tweets.count_documents({})
