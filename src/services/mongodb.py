import os
import json
import pymongo
from pymongo import database

from .secret import get_json_secret_from_gcp


def get_mongodb_connection(*, gcp_secret_name: str) -> database.Database:
    """Connects to MongoDB based on credentials read from
    GCP Secret Manager or Environment variable

    Args:
        gcp_secret_name (str): A secret name in GCP Secret Manager
        OR environment variable containing that secret name.

        Note: GCP secret name has format: projects/*/secrets/*/versions/*

    Returns:
        pymongo.database.Database: A connection to MongoDB.

    Raises:
        json.JSONDecodeError: If the secret value is not valid json.

    """
    if not gcp_secret_name.startswith("projects/"):
        if gcp_secret_name not in os.environ:
            raise ValueError(
                "Failed to connect to MongoDB: missing environment "
                f'variable "{gcp_secret_name}" containing MongoDB credentials.'
            )
        gcp_secret_name = os.environ[gcp_secret_name]

    if gcp_secret_name.startswith("projects/"):
        mongo_secret = get_json_secret_from_gcp(gcp_secret_name)
    else:
        mongo_secret = json.loads(gcp_secret_name)

    user = mongo_secret["DB_USER"]
    password = mongo_secret["DB_PASS"]
    hostname = mongo_secret["DB_HOSTNAME"]
    db_name = mongo_secret["DB_NAME"]
    scheme = mongo_secret.get("SCHEME", "mongodb+srv")
    db_url = (
        f"{scheme}://{user}:{password}@{hostname}/{db_name}?"
        "retryWrites=true&w=majority"
    )

    return pymongo.MongoClient(db_url).get_database(db_name)
