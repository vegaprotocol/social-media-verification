import ed25519
import hashlib
import base64
import pymongo
import json
import sys
import warnings
import os
import time

from twython import Twython

if not sys.warnoptions:
    warnings.simplefilter("ignore")

consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_secret = os.environ['TWITTER_ACCESS_SECRET']
twitter_search_text = os.environ['TWITTER_SEARCH_TEXT']
format_invalid_reply = os.environ['FORMAT_INVALID_REPLY']
signature_invalid_reply = os.environ['SIGNATURE_INVALID_REPLY']
mongo_host = os.environ['MONGO_HOST']
mongo_port = os.environ['MONGO_PORT']
mongo_user = os.environ['MONGO_USER']
mongo_password = os.environ['MONGO_PASSWORD']
sleep_duration = int(os.environ['SLEEP_DURATION'])

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
    client = pymongo.MongoClient(f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}")
    db = client["admin"]
    return db[name]
    
def store_verified_party(screen_name, pub_key):
    collection = get_db_collection("identities")
    query = {"pub_key": pub_key}
    doc = collection.find(query)
    if doc.count() == 0:
        collection.insert_one({"twitter_handle": screen_name, "pub_key": pub_key})
    else:
        collection.update_one(query, {"$set": {"twitter_handle": screen_name}})

def store_tweet_record(tweet_id, screen_name, status):
    collection = get_db_collection("tweets")
    query = {"tweet_id": tweet_id}
    doc = collection.find(query)
    if doc.count() == 0:
        collection.insert_one({"tweet_id": tweet_id, "status": status, "screen_name": screen_name})

def is_tweet_processed(tweet_id):
    collection = get_db_collection("tweets")
    query = {"tweet_id": tweet_id}
    doc = collection.find(query)
    if doc.count() == 0:
        return False
    return True

def process_tweet(tweet, twapi):
    try:
        tweet_id = tweet['id']
        tweet_processed = is_tweet_processed(tweet_id)
        if not tweet_processed:
            screen_name = tweet['user']['screen_name']
            full_text = tweet['full_text']
            tweet_parts = list(filter(lambda x: len(x) > 0, full_text.replace('\n', ' ').split(' ')))
            sig = tweet_parts[-1]
            pub_key = tweet_parts[-2]
            sig_valid = is_sig_valid(sig, screen_name, pub_key)
            if sig_valid:
                store_verified_party(screen_name, pub_key)
                store_tweet_record(tweet_id, screen_name, "PASSED")
                print("signature verified!")
            else:
                print("invalid sig")
                store_tweet_record(tweet_id, screen_name, "INVALID")
                msg = f'@{screen_name} {signature_invalid_reply}'
                twapi.update_status(status=msg, in_reply_to_status_id=tweet_id)
        else:
            print("tweet already processed")
    except:
        print("cannot parse tweet")
        msg = f'@{screen_name} {format_invalid_reply}'
        twapi.update_status(status=msg, in_reply_to_status_id=tweet_id)
        store_tweet_record(tweet_id, screen_name, "UNPARSEABLE")

def search_tweets():
    twapi = Twython(consumer_key, consumer_secret, access_token, access_secret)
    try:
        results = twapi.search(q=twitter_search_text, count=50, tweet_mode='extended')
    except TwythonError as e:
        print(e)
        return
    results['statuses'].reverse()
    tweet_count = len(results['statuses'])
    print(f'Found {tweet_count} tweets')
    for tweet in results['statuses']:
        process_tweet(tweet, twapi)

while True:
    search_tweets()
    time.sleep(sleep_duration)

