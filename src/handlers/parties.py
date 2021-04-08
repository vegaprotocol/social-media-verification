import flask
from pymongo import database
from helpers.onelog import onelog_json, OneLog


@onelog_json
def handle_parties(
    db: database.Database, onelog: OneLog = None
) -> flask.Response:
    parties = []
    collection = db.get_collection("identities")
    for item in collection.find():
        parties.append(
            {
                "party_id": item["pub_key"],
                "twitter_handle": item["twitter_handle"],
            }
        )

    onelog.info(parties_count=len(parties))

    return flask.jsonify(parties)
