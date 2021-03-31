import ed25519
import hashlib
import base64
import pymongo
import sys
import warnings
import os
import time
import flask
import traceback
from timeit import default_timer as timer

from twython import Twython
from helper import get_json_secret, get_mongodb_url_from_secret

if not sys.warnoptions:
    warnings.simplefilter("ignore")

#
# Setup MongoDB connection
#
mongo_secret_name = os.environ["MONGO_SECRET_NAME"]
mongo_secret = get_json_secret(mongo_secret_name)
db_name = mongo_secret["DB_NAME"]
DB_URL = get_mongodb_url_from_secret(mongo_secret)

DB_CONN = pymongo.MongoClient(DB_URL).get_database(db_name)

#
# Setup Twitter Access Token
#
twitter_secret_name = os.environ["TWITTER_SECRET_NAME"]
twitter_secret = get_json_secret(twitter_secret_name)
# Load from secret
TWITTER_CONSUMER_KEY = twitter_secret["CONSUMER_KEY"]
TWITTER_CONSUMER_SECRET = twitter_secret["CONSUMER_SECRET"]
TWITTER_ACCESS_TOKEN = twitter_secret["ACCESS_TOKEN"]
TWITTER_ACCESS_SECRET = twitter_secret["ACCESS_SECRET"]
# Load from env variables
TWITTER_SEARCH_TEXT = os.environ["TWITTER_SEARCH_TEXT"]
TWITTER_REPLY_SUCCESS = os.environ["TWITTER_REPLY_SUCCESS"]
TWITTER_REPLY_INVALID_FORMAT = os.environ["TWITTER_REPLY_INVALID_FORMAT"]
TWITTER_REPLY_INVALID_SIGNATURE = os.environ["TWITTER_REPLY_INVALID_SIGNATURE"]


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


def get_db_collection(name):
    return DB_CONN.get_collection(name)


def store_verified_party(screen_name, pub_key):
    collection = get_db_collection("identities")
    query = {"pub_key": pub_key}
    doc = collection.find(query)
    if doc.count() == 0:
        collection.insert_one(
            {"twitter_handle": screen_name, "pub_key": pub_key},
        )
    else:
        collection.update_one(query, {"$set": {"twitter_handle": screen_name}})


def store_tweet_record(tweet_id, screen_name, status):
    collection = get_db_collection("tweets")
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


def is_tweet_processed(tweet_id):
    collection = get_db_collection("tweets")
    query = {"tweet_id": tweet_id}
    doc = collection.find(query)
    if doc.count() == 0:
        return False
    return True


def get_parties():
    start_time = timer()
    log_line = "Get Parties"
    try:
        collection = get_db_collection("identities")
        doc = collection.find()
        parties = []
        for item in doc:
            parties.append(
                {
                    "party_id": item["pub_key"],
                    "twitter_handle": item["twitter_handle"],
                }
            )
        log_line += f', parties_count={len(parties)}, status="SUCCESS"'
        return parties
    except Exception as err:
        log_line += f', error="{err}", status="ERROR"'
        raise
    finally:
        end_time = timer()
        elapsed_time_ms = int((end_time - start_time) * 1000)
        log_line += f', time_ms="{elapsed_time_ms}"'
        print(log_line)


def process_tweet(tweet, twapi):
    start_time = timer()
    log_line = f"Processing tweet={tweet}"
    replied_to_user = False
    try:
        tweet_id = tweet["id"]
        tweet_processed = is_tweet_processed(tweet_id)
        log_line += (
            f', tweet_id="{tweet_id}", tweet_processed="{tweet_processed}"'
        )
        if not tweet_processed:
            screen_name = tweet["user"]["screen_name"]
            full_text = tweet["full_text"]
            log_line += (
                f', screen_name="{screen_name}", full_text="{full_text}"'
            )
            tweet_parts = list(
                filter(
                    lambda x: len(x) > 0,
                    full_text.replace("\n", " ").split(" "),
                )
            )
            sig = tweet_parts[-1]
            pub_key = tweet_parts[-2]
            sig_valid = is_sig_valid(sig, screen_name, pub_key)
            log_line += (
                f', sig="{sig}", pub_key="{pub_key}"'
                f', sig_valid="{sig_valid}"'
            )
            if sig_valid:
                store_verified_party(screen_name, pub_key)
                store_tweet_record(tweet_id, screen_name, "PASSED")
                msg = f"@{screen_name} {TWITTER_REPLY_SUCCESS}"
                log_line += f', reply_msg="{msg}"'
                twapi.update_status(status=msg, in_reply_to_status_id=tweet_id)
                replied_to_user = True
                log_line += ', status="SUCCESS"'
            else:
                store_tweet_record(tweet_id, screen_name, "INVALID")
                msg = f"@{screen_name} {TWITTER_REPLY_INVALID_SIGNATURE}"
                log_line += f', reply_msg="{msg}"'
                twapi.update_status(status=msg, in_reply_to_status_id=tweet_id)
                replied_to_user = True
                log_line += ', status="INVALID"'
        else:
            log_line += ', status="SKIP"'
            replied_to_user = False
    except Exception as err:
        traceback.print_exc()
        print(err)
        msg = f"@{screen_name} {TWITTER_REPLY_INVALID_FORMAT}"
        log_line += f', error="{err}", reply_msg="{msg}"'
        twapi.update_status(status=msg, in_reply_to_status_id=tweet_id)
        replied_to_user = True
        store_tweet_record(tweet_id, screen_name, "UNPARSEABLE")
        log_line += ', status="ERROR"'
    finally:
        end_time = timer()
        elapsed_time_ms = int((end_time - start_time) * 1000)
        log_line += f', time_ms="{elapsed_time_ms}"'
        print(log_line)

    return replied_to_user


def search_tweets(twapi: Twython) -> list:
    start_time = timer()
    log_line = "Searching tweets"
    try:
        results = twapi.search(
            q=TWITTER_SEARCH_TEXT, count=50, tweet_mode="extended"
        )
        tweets = list(reversed(results["statuses"]))
        log_line += f', tweets_count="{len(tweets)}", status="SUCCESS"'
        return tweets
    except Exception as err:
        log_line += f', error="{err}", status="ERROR"'
        raise
    finally:
        end_time = timer()
        elapsed_time_ms = int((end_time - start_time) * 1000)
        log_line += f', time_ms="{elapsed_time_ms}"'
        print(log_line)


def process_tweets(twapi: Twython, tweets: list):
    start_time = timer()
    log_line = f'Processing tweets count="{len(tweets)}"'
    try:
        response_count = 0
        for tweet in tweets:
            replied_to_user = process_tweet(tweet, twapi)
            if replied_to_user:
                response_count += 1
                # sleep for 1 second after replying to user
                time.sleep(1)
        log_line += f', response_count="{response_count}", status="SUCCESS"'
    except Exception as err:
        log_line += f', error="{err}", status="ERROR"'
        raise
    finally:
        end_time = timer()
        elapsed_time_ms = int((end_time - start_time) * 1000)
        log_line += f', time_ms="{elapsed_time_ms}"'
        print(log_line)


def handle_request(request: flask.Request):
    if request.path.endswith("/parties"):
        return flask.jsonify(get_parties())
    elif request.path.endswith("/process-tweets"):
        try:
            twapi = Twython(
                TWITTER_CONSUMER_KEY,
                TWITTER_CONSUMER_SECRET,
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_SECRET,
            )
            tweets = search_tweets(twapi)
            process_tweets(twapi, tweets)
            return flask.jsonify({"status": "success"})
        except Exception as err:
            traceback.print_exc()
            print(err)
            return flask.jsonify({"status": "failed", "error": str(err)}), 500
    else:
        flask.abort(404, description="Resource not found")
