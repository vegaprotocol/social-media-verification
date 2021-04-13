from pymongo import database
from pymongo.collection import Collection
from .mongodb import get_mongodb_connection


class SMVStore(object):
    """Access SMV Store (currently backed with MongoDB)"""

    def __init__(self, db: database.Database) -> None:
        self.db = db

    @classmethod
    def get_store(cls, *, gcp_secret_name: str) -> "SMVStore":
        return SMVStore(
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
            }
            for item in self.col_identities.find()
        ]
