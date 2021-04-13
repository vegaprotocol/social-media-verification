import flask
import os
from services.smv_store import SMVStore
from handlers import handle_parties
from handlers.process_tweets import handle_process_tweets

store = SMVStore(
    gcp_secret_name=os.environ["MONGO_SECRET_NAME"],
)


def router(request: flask.Request):
    if request.path.endswith("/parties"):
        return handle_parties(store=store)
    elif request.path.endswith("/process-tweets"):
        return handle_process_tweets(db=store.db)
    else:
        flask.abort(404, description="Resource not found")
