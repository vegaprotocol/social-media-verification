import pytest
import os
from services.smv_storage import SMVStorage


@pytest.fixture(scope="session", autouse=True)
def smv_storage() -> SMVStorage:
    MONGO_DB_USER = os.getenv("MONGO_DB_USER")
    MONGO_DB_PASS = os.getenv("MONGO_DB_PASS")
    MONGO_DB_HOSTNAME = os.getenv("MONGO_DB_HOSTNAME")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    if (
        not MONGO_DB_USER
        or not MONGO_DB_PASS
        or not MONGO_DB_HOSTNAME
        or not MONGO_DB_NAME
    ):
        return None

    assert "local" in MONGO_DB_NAME

    os.environ[
        "MONGO_SECRET"
    ] = f"""{{
        "DB_USER": "{MONGO_DB_USER}",
        "DB_PASS": "{MONGO_DB_PASS}",
        "DB_HOSTNAME": "{MONGO_DB_HOSTNAME}",
        "DB_NAME": "{MONGO_DB_NAME}",
        "SCHEME": "mongodb"
    }}"""

    try:
        return SMVStorage.get_storage(gcp_secret_name="MONGO_SECRET")
    except:
        pass
    return None


@pytest.fixture(autouse=True)
def process_skipif_no_mongodb(request, smv_storage):
    if smv_storage is None:
        marker = request.node.get_closest_marker("skipif_no_mongodb")
        if marker is not None:
            pytest.skip(f"No mongodb connection available.")


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "skipif_no_mongodb: skip test if there is no mongodb available",
    )
