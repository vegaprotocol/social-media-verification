from typing import Any, Optional, Dict, List
import pymongo
from pymongo import database
from pymongo.collection import Collection
from pymongo.cursor import CursorType
from datetime import datetime, timezone
from .mongodb import get_mongodb_connection

from common import BlocklistPartyError


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

    @property
    def col_todo_tweets(self) -> Collection:
        return self.db.get_collection("todo_tweets")

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
                "created": int(
                    item["created"].replace(tzinfo=timezone.utc).timestamp()
                ),
            }
            for item in self.col_identities.find(
                cursor_type=CursorType.EXHAUST
            )
            if item.get("blocked", None) is None
        ]

    def upsert_verified_party(
        self,
        pub_key: str,
        user_id: int,
        screen_name: str,
    ):
        now = datetime.utcnow().replace(tzinfo=timezone.utc)

        # Check if pub_key and user_id belong to two different participants
        # already registered.
        # This is to detect if pub_key is moved from one party to another
        # if so, then we block both parties
        existing_parties_count = self.col_identities.count_documents(
            {
                "$or": [
                    {"pub_key": pub_key},
                    {"twitter_user_id": user_id},
                ],
            }
        )
        if existing_parties_count > 1:
            err_msg = "Sign up matched multiple parties:"
            err_msg += f" twitter_id: '{user_id}', pub_key: '{pub_key}'"
            self.col_identities.update_many(
                {
                    "$or": [
                        {"pub_key": pub_key},
                        {"twitter_user_id": user_id},
                    ],
                },
                {
                    "$set": {
                        "blocked": err_msg,
                        "last_modified": now,
                    },
                },
            )
            raise BlocklistPartyError(err_msg)

        # Check if participant is not blocked
        blocked_party = self.col_identities.find_one(
            {
                "$or": [
                    {"pub_key": pub_key},
                    {"twitter_user_id": user_id},
                ],
                "blocked": {"$ne": None},
            }
        )
        if blocked_party:
            raise BlocklistPartyError(
                f"Participant (twitter_id: {blocked_party['twitter_user_id']})"
                f" is blocked with"
                f" reason: '{blocked_party['blocked']}'. Ignoring sign-up:"
                f" twitter_id: '{user_id}', pub_key: '{pub_key}'"
            )

        self.col_identities.update_one(
            {
                "$nor": [
                    {
                        "twitter_handle": screen_name,
                        "pub_key": {"$ne": pub_key},
                        "twitter_user_id": {"$ne": user_id},
                    }
                ],
                "$or": [
                    {"pub_key": pub_key},
                    {"twitter_user_id": user_id},
                    {"twitter_handle": screen_name},
                ],
            },
            {
                "$set": {
                    "pub_key": pub_key,
                    "twitter_user_id": user_id,
                    "twitter_handle": screen_name,
                    "last_modified": now,
                    "blocked": None,
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
        description: str = None,
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
        if description is not None:
            data["description"] = description
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

    def add_todo_tweet(self, tweet_id: int):
        self.col_todo_tweets.insert_one({"tweet_id": tweet_id})

    def get_todo_tweets(self, limit: int = 50) -> List[int]:
        return list(
            set(
                [
                    item["tweet_id"]
                    for item in self.col_todo_tweets.find(
                        limit=limit,
                    )
                ]
            )
        )

    def cleanup_todo_tweets(self) -> None:
        tweet_ids = [
            item["tweet_id"]
            for item in self.col_todo_tweets.aggregate(
                [
                    {
                        "$lookup": {
                            "from": "tweets",
                            "localField": "tweet_id",
                            "foreignField": "tweet_id",
                            "as": "processed_tweets",
                        }
                    },
                    {"$match": {"processed_tweets": {"$ne": []}}},
                ]
            )
        ]
        if tweet_ids:
            self.col_todo_tweets.delete_many({"tweet_id": {"$in": tweet_ids}})
