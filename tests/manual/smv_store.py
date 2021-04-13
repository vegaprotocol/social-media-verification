#!/usr/bin/env python3
import os

from services.smv_store import SMVStore

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

store = SMVStore.get_store(gcp_secret_name="MONGO_SECRET")

print(f"parties={store.get_parties()}")
