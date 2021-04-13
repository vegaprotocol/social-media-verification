import flask
from services.smv_storage import SMVStorage
from services.onelog import onelog_json, OneLog


@onelog_json
def handle_parties(storage: SMVStorage, onelog: OneLog = None) -> flask.Response:
    parties = storage.get_parties()
    onelog.info(parties_count=len(parties))
    return flask.jsonify(parties)
