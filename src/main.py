import flask
import os
from helpers.mongodb import get_mongodb_connection
from handlers import handle_parties
from app import handle_process_tweets

DB = get_mongodb_connection(
    gcp_secret_name=os.environ["MONGO_SECRET_NAME"],
)


def router(request: flask.Request):
    if request.path.endswith("/parties"):
        return handle_parties(db=DB)
    elif request.path.endswith("/process-tweets"):
        return handle_process_tweets()
    else:
        flask.abort(404, description="Resource not found")
