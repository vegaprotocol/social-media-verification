import json

def get_json_secret(secret_name: str) -> dict:
    from google.cloud import secretmanager
    
    client = secretmanager.SecretManagerServiceClient()
    request = {"name": secret_name}
    response = client.access_secret_version(request)
    payload =  response.payload.data.decode("UTF-8")
    return json.loads(payload)

def get_mongodb_url_from_secret(secret: dict) -> str:
    user = secret['DB_USER']
    password = secret['DB_PASS']
    hostname = secret['DB_HOSTNAME']
    db_name = secret['DB_NAME']
    return (
        f"mongodb+srv://{user}:{password}@{hostname}/{db_name}?"
        "retryWrites=true&w=majority"
    )
