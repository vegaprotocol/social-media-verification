#!/usr/bin/env python3
import flask
from smv_storage import storage
from handlers import handle_parties

if __name__ == "__main__":

    app = flask.Flask("test")

    print("------ EXECUTION LOGS: begin ------")
    with app.test_request_context():
        response = handle_parties(storage)  # type: flask.Response
    print("------ EXECUTION LOGS: ------")

    print("Results:")
    print(f"\tstatus_code={response.status_code}")
    print(f"\tresponse={response.json}")
