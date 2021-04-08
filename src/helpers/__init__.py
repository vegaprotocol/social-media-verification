import json


def get_json_secret(secret_name: str) -> dict:
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    request = {"name": secret_name}
    response = client.access_secret_version(request)
    payload = response.payload.data.decode("UTF-8")
    return json.loads(payload)
