import flask
from smv.app import handle_parties, handle_process_tweets


def router(request: flask.Request):
    if request.path.endswith("/parties"):
        return handle_parties()
    elif request.path.endswith("/process-tweets"):
        return handle_process_tweets()
    else:
        flask.abort(404, description="Resource not found")
