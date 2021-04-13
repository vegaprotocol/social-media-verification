import ed25519
import hashlib
import base64
import flask
from pymongo import database
import traceback
from services.twitter import TwitterClient, Tweet
from services.smv_store import SMVStore
from common import SMVConfig
from services.onelog import onelog_json, OneLog


def is_sig_valid(sig, msg, pub_key):
    verifying_key = ed25519.VerifyingKey(bytes.fromhex(pub_key))
    s = hashlib.sha3_256()
    s.update(bytes(msg, "UTF-8"))
    msg = s.digest()
    bytesig = base64.b64decode(sig)
    try:
        verifying_key.verify(bytesig, msg)
        return True
    except ed25519.BadSignatureError:
        return False
    return False


def store_verified_party(db: database.Database, screen_name, pub_key):
    collection = db.get_collection("identities")
    query = {"pub_key": pub_key}
    doc = collection.find(query)
    if doc.count() == 0:
        collection.insert_one(
            {"twitter_handle": screen_name, "pub_key": pub_key},
        )
    else:
        collection.update_one(query, {"$set": {"twitter_handle": screen_name}})


def store_tweet_record(db: database.Database, tweet_id, screen_name, status):
    collection = db.get_collection("tweets")
    query = {"tweet_id": tweet_id}
    doc = collection.find(query)
    if doc.count() == 0:
        collection.insert_one(
            {
                "tweet_id": tweet_id,
                "status": status,
                "screen_name": screen_name,
            }
        )


def is_tweet_processed(db: database.Database, tweet_id):
    collection = db.get_collection("tweets")
    query = {"tweet_id": tweet_id}
    doc = collection.find(query)
    if doc.count() == 0:
        return False
    return True


@onelog_json
def process_tweet(
    tweet: Tweet,
    store: SMVStore,
    twclient: TwitterClient,
    config: SMVConfig,
    onelog: OneLog = None,
):
    onelog.info(
        tweet_id=tweet.tweet_id,
        tweet_user=tweet.user_id,
        tweet_message=tweet.full_text,
    )

    tweet_processed = is_tweet_processed(store.db, tweet.tweet_id)
    onelog.info(tweet_processed=tweet_processed)

    if tweet_processed:
        onelog.info(status="SKIP")
    else:
        onelog.info(status="PROCESSING")


@onelog_json
def handle_process_tweets(
    store: SMVStore,
    twclient: TwitterClient,
    config: SMVConfig,
    onelog: OneLog = None,
):
    # Fetch all tweets from Twitter API
    try:
        # TODO: use since_tweet_id (get it from mongo db)
        tweets = list(
            twclient.search(
                config.twitter_search_text,
            )
        )
        onelog.info(total_count=len(tweets))
    except Exception as err:
        onelog.info(error=str(err), status="FAILED")
        traceback.print_exc()
        print(err)
        return (
            flask.jsonify(
                {"status": "failed", "error": "Failed to fetch tweets."}
            ),
            500,
        )

    # Process tweets one by one from oldest to newest
    try:
        processed_count = 0
        for twt in reversed(tweets):
            process_tweet(
                twt,
                store,
                twclient,
                config,
            )
            processed_count += 1
        onelog.info(processed_count=processed_count)
    except Exception as err:
        onelog.info(
            processed_count=processed_count, error=str(err), status="FAILED"
        )
        traceback.print_exc()
        print(err)
        return flask.jsonify({"status": "failed", "error": str(err)}), 500

    return flask.jsonify({"status": "success"})
