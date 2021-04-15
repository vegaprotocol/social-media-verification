#!/usr/bin/env python3
import os

from services.smv_storage import SMVStorage

MONGO_DB_USER = "[DATABASE USERNAME]"
MONGO_DB_PASS = "[DATABASE USERNAME PASSWORD]"
MONGO_DB_HOSTNAME = "[DATABASE CONNECTION HOSTNAME]"
MONGO_DB_NAME = "[DATABASE NAME]"

os.environ[
    "MONGO_SECRET"
] = f"""{{
    "DB_USER": "{MONGO_DB_USER}",
    "DB_PASS": "{MONGO_DB_PASS}",
    "DB_HOSTNAME": "{MONGO_DB_HOSTNAME}",
    "DB_NAME": "{MONGO_DB_NAME}"
}}"""

storage = SMVStorage.get_storage(gcp_secret_name="MONGO_SECRET")

print(f"parties={storage.get_parties()}")

# storage.upsert_tweet_record(1233, text="gg", screen_name="abc_userrrrrr")

print(f"tweet_record={storage.get_tweet_record(1233)}")

print(f"get_tweet_count_by_status={storage.get_tweet_count_by_status()}")

print(f"get_last_tweet_id={storage.get_last_tweet_id()}")
