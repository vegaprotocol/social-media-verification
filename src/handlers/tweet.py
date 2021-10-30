import flask
from services.smv_storage import SMVStorage
from services.onelog import onelog_json, OneLog


@onelog_json
def handle_tweet(
    storage: SMVStorage, tweet_id: str, onelog: OneLog = None
) -> flask.Response:
    onelog.info(tweet_id=tweet_id)

    if not tweet_id:
        return flask.jsonify(
            {"status": "failed", "error": "Missing id argument in the request"}
        )

    if isinstance(tweet_id, str):
        if not tweet_id.isdigit():
            return flask.jsonify(
                {
                    "status": "failed",
                    "tweet_id": tweet_id,
                    "error": "id argument must contain digits only",
                }
            )
        tweet_id = int(tweet_id)

    if not isinstance(tweet_id, int):
        return flask.jsonify(
            {
                "status": "failed",
                "tweet_id": tweet_id,
                "error": "id argument must contain digits only",
            }
        )

    processed_tweet = storage.get_tweet_record(tweet_id)
    if processed_tweet:
        del processed_tweet["_id"]
        # add extra info
        description = {
            "PROCESSING": "The tweet is being processed.",
            "PASSED": "Successful sign up",
            "INVALID_FORMAT": "The tweet does not look like a sign up tweet.",
            "INVALID_SIGNATURE": (
                "Signature does not match user's twitter handle: make sure"
                " user signed their twitter handle not name, i.e."
                " @twitter_handle - it starts with @. Other common mistakes"
                " are typo, wrong lower-upper case."
            ),
            "BLOCKLISTED": (
                "User tried to do something not allowed, e.g. transfer Wallet"
                " to another user"
            ),
        }
        processed_tweet["status_description"] = description.get(
            processed_tweet["status"]
        )
        return flask.jsonify(
            {
                "status": "success",
                "tweet_id": tweet_id,
                "message": "Tweet has been already processed",
                "tweet": processed_tweet,
            }
        )

    if storage.is_todo_tweet(tweet_id):
        return flask.jsonify(
            {
                "status": "success",
                "tweet_id": tweet_id,
                "message": "Tweet is waiting to be processed",
            }
        )

    storage.add_todo_tweet(tweet_id)
    return flask.jsonify(
        {
            "status": "success",
            "tweet_id": tweet_id,
            "message": "Tweet added to the queue to be processed",
        }
    )
