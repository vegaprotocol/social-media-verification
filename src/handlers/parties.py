import flask
from services.smv_store import SMVStore
from services.onelog import onelog_json, OneLog


@onelog_json
def handle_parties(store: SMVStore, onelog: OneLog = None) -> flask.Response:
    parties = store.get_parties()
    onelog.info(parties_count=len(parties))
    return flask.jsonify(parties)
