from typing import Tuple
import ed25519
import hashlib
import base64
import flask
import traceback
import re
import time
from services.twitter import TwitterClient, Tweet
from services.smv_storage import SMVStorage
from common import (
    SMVConfig,
    TweetInvalidFormatError,
    TweetInvalidSignatureError,
)
from services.onelog import onelog_json, OneLog


def is_sig_valid(sig, msg, pub_key):
    try:
        verifying_key = ed25519.VerifyingKey(bytes.fromhex(pub_key))
        s = hashlib.sha3_256()
        s.update(bytes(msg, "UTF-8"))
        msg = s.digest()
        bytesig = base64.b64decode(sig)
        verifying_key.verify(bytesig, msg)
        return True
    except (ed25519.BadSignatureError, Exception):
        return False
    return False


def parse_message(msg: str, prefix: str) -> Tuple[str, str]:
    m = re.match(
        fr"^{prefix}\s+(?P<PUBKEY>[0-9a-fA-F]+)\s+(?P<SIGNED_MESSAGE>[^\s]+)",
        msg,
    )
    if not m:
        raise TweetInvalidFormatError("Wrong format")

    return m.group("PUBKEY"), m.group("SIGNED_MESSAGE")


def validate_signature(pubkey: str, signed_message: str, twitter_handle: str):
    for msg in [twitter_handle, f"@{twitter_handle}"]:
        if is_sig_valid(sig=signed_message, msg=msg, pub_key=pubkey):
            return
    raise TweetInvalidSignatureError("Invalid signature")


@onelog_json
def process_tweet(
    tweet: Tweet,
    storage: SMVStorage,
    twclient: TwitterClient,
    config: SMVConfig,
    tweet_prefix: str,
    onelog: OneLog = None,
):
    onelog.info(
        tweet_id=tweet.tweet_id,
        tweet_handle=tweet.user_screen_name,
        tweet_user_id=tweet.user_id,
        tweet_message=tweet.full_text,
    )

    if storage.get_tweet_record(tweet.tweet_id) is not None:
        onelog.info(tweet_processed=True, status="SKIP")
    else:
        storage.upsert_tweet_record(
            tweet_id=tweet.tweet_id,
            user_id=tweet.user_id,
            screen_name=tweet.user_screen_name,
            text=tweet.full_text,
            status="PROCESSING",
        )
        try:
            pubkey, signed_message = parse_message(
                tweet.full_text, tweet_prefix
            )
            onelog.info(pubkey=pubkey, signed_message=signed_message)
            validate_signature(
                pubkey,
                signed_message,
                twitter_handle=tweet.user_screen_name,
            )
            # Do not reply to user on Twitter
            # update DB - verified party
            storage.upsert_verified_party(
                pubkey,
                tweet.user_id,
                tweet.user_screen_name,
            )
            # update DB
            storage.upsert_tweet_record(
                tweet_id=tweet.tweet_id,
                reply="",
                status="PASSED",
            )

        except TweetInvalidFormatError:
            onelog.info(error="Invalid Format", status="FAILED")
            # reply on twitter
            # Do not reply to user on Twitter
            # update DB
            storage.upsert_tweet_record(
                tweet_id=tweet.tweet_id,
                reply="",
                status="INVALID_FORMAT",
            )
        except TweetInvalidSignatureError:
            onelog.info(error="Invalid Signature", status="FAILED")
            # reply on twitter
            time.sleep(config.twitter_reply_delay)
            twclient.reply(
                config.twitter_reply_message_invalid_signature,
                tweet,
            )
            # update DB
            storage.upsert_tweet_record(
                tweet_id=tweet.tweet_id,
                reply=config.twitter_reply_message_invalid_signature,
                status="INVALID_SIGNATURE",
            )


@onelog_json
def handle_process_tweets(
    storage: SMVStorage,
    twclient: TwitterClient,
    config: SMVConfig,
    onelog: OneLog = None,
):
    # Fetch all tweets from Twitter API
    try:
        twitter_search_text = (
            f"{config.twitter_search_text} @{twclient.account_name}"
        )
        onelog.info(twitter_search_text=twitter_search_text)
        since_tweet_id = storage.get_last_tweet_id()
        onelog.info(since_tweet_id=since_tweet_id)
        tweets = list(
            twclient.get_tweets(
                twitter_search_text, since_tweet_id,
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
                storage,
                twclient,
                config,
                tweet_prefix=twitter_search_text,
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
