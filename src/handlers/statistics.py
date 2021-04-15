import flask
from datetime import datetime, timezone
from services.smv_storage import SMVStorage
from services.onelog import onelog_json, OneLog


@onelog_json
def handle_statistics(
    storage: SMVStorage, onelog: OneLog = None
) -> flask.Response:
    return flask.jsonify(
        {
            "time": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "tweet_status_count": storage.get_tweet_count_by_status(),
            "last_tweet_id": storage.get_last_tweet_id(),
        }
    )
