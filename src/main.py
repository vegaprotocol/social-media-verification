import flask
import os
from common import SMVConfig
from services.smv_store import SMVStore
from handlers import handle_parties
from handlers.process_tweets import handle_process_tweets
from services.twitter import TwitterClient

CONFIG = SMVConfig(
    twitter_search_text=os.environ["TWITTER_SEARCH_TEXT"],
    twitter_reply_message_success=os.environ["TWITTER_REPLY_SUCCESS"],
    twitter_reply_message_invalid_format=os.environ[
        "TWITTER_REPLY_INVALID_FORMAT"
    ],
    twitter_reply_message_invalid_signature=os.environ[
        "TWITTER_REPLY_INVALID_SIGNATURE"
    ],
    twitter_reply_delay=float(os.getenv("TWITTER_REPLY_DELAY", "0.25")),
)

STORE = SMVStore.get_store(
    gcp_secret_name=os.environ["MONGO_SECRET_NAME"],
)

TWCLIENT = TwitterClient(
    gcp_secret_name=os.environ["TWITTER_SECRET_NAME"],
)


def router(request: flask.Request):
    if request.path.endswith("/parties"):
        return handle_parties(store=STORE)
    elif request.path.endswith("/process-tweets"):
        return handle_process_tweets(
            store=STORE,
            twclient=TWCLIENT,
            config=CONFIG,
        )
    else:
        flask.abort(404, description="Resource not found")
