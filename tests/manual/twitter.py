#!/usr/bin/env python3
import os

from services.twitter import TwitterClient

TWITTER_ACCOUNT_NAME = "[PUT TWITTER ACCOUNT NAME WITHOUT @]"
TWITTER_APP_KEY = "[PUT APP KEY/CONSUMER KEY]"
TWITTER_APP_SECRET = "[PUT APP SECRET/CONSUMER SECRET]"

TWITTER_SEARCH_TEXT = "Here comes the party"

os.environ[
    "TWITTER_SECRET"
] = f"""{{
    "ACCOUNT_NAME": "{TWITTER_ACCOUNT_NAME}",
    "CONSUMER_KEY": "{TWITTER_APP_KEY}",
    "CONSUMER_SECRET": "{TWITTER_APP_SECRET}"
}}"""

twclient = TwitterClient(
    gcp_secret_name="TWITTER_SECRET",
)

i = 0
for tweet in reversed(list(twclient.search(TWITTER_SEARCH_TEXT))):
    i += 1
    print(f" ------ {i} {tweet}")
