#!/usr/bin/env python3
import os

from services.twitter import TwitterClient

TWITTER_ACCOUNT_NAME = "ACC NAME"
TWITTER_APP_KEY = "PUT APP KEY"
TWITTER_APP_SECRET = "PUT APP SECRET"

TWITTER_SEARCH_TEXT = "Here comes the party"

os.environ[
    "TWITTER_SECRET"
] = f"""{{
    "ACCOUNT_NAME": "{TWITTER_ACCOUNT_NAME}",
    "APP_KEY": "{TWITTER_APP_KEY}",
    "APP_SECRET": "{TWITTER_APP_SECRET}"
}}"""

twclient = TwitterClient(
    gcp_secret_name="TWITTER_SECRET",
)

i = 0
for tweet in reversed(list(twclient.search(TWITTER_SEARCH_TEXT))):
    i += 1
    print(f" ------ {i} {tweet}")
