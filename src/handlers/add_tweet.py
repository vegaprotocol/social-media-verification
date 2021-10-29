import flask
from services.smv_storage import SMVStorage
from services.onelog import onelog_json, OneLog


@onelog_json
def handle_add_tweet(
    storage: SMVStorage, tweet_id: int, onelog: OneLog = None
) -> flask.Response:
    onelog.info(tweet_id=tweet_id)
    storage.add_todo_tweet(tweet_id)
    return flask.jsonify({"status": "success", "tweet_id": tweet_id})
