#!/usr/bin/env python3
import os

from services.twitter import TwitterClient
from handlers.process_tweets import parse_message, validate_signature

TWITTER_ACCOUNT_NAME = "[PUT TWITTER ACCOUNT NAME WITHOUT @]"
TWITTER_CONSUMER_KEY = "[PUT TWITTER APP KEY/CONSUMER KEY]"
TWITTER_CONSUMER_SECRET = "[PUT TWITTER APP SECRET/CONSUMER SECRET]"
TWITTER_ACCESS_TOKEN = "[PUT TWITTER USER ACCESS TOKEN"
TWITTER_ACCESS_SECRET = "[PUT TWITTER USER ACCESS SECRET]"

TWITTER_SEARCH_TEXT = f"I'm taking a ride on @{TWITTER_ACCOUNT_NAME}"

os.environ[
    "TWITTER_SECRET"
] = f"""{{
    "ACCOUNT_NAME": "{TWITTER_ACCOUNT_NAME}",
    "CONSUMER_KEY": "{TWITTER_CONSUMER_KEY}",
    "CONSUMER_SECRET": "{TWITTER_CONSUMER_SECRET}",
    "ACCESS_TOKEN": "{TWITTER_ACCESS_TOKEN}",
    "ACCESS_SECRET": "{TWITTER_ACCESS_SECRET}"
}}"""

twclient = TwitterClient(
    gcp_secret_name="TWITTER_SECRET",
)

if __name__ == "__main__":
    i = 0
    for tweet in twclient.get_tweets(TWITTER_SEARCH_TEXT):
        try:
            parsed = "not parsable"
            pubkey, signed_message = parse_message(
                tweet.full_text,
                TWITTER_SEARCH_TEXT,
            )
            parsed = "invalid signature"
            validate_signature(
                pubkey,
                signed_message,
                twitter_handle=tweet.user_screen_name,
            )
            parsed = "OK"
        except Exception:
            pass
        i += 1
        print(
            f" ------ {i} [{parsed}]: {tweet}, url: https:"
            f"//twitter.com/{tweet.user_screen_name}/status/{tweet.tweet_id}"
        )
