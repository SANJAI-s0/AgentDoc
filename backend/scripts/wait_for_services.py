import os
import socket
import sys
import time

from pymongo import MongoClient


def wait_for_port(host: str, port: int, timeout_seconds: int = 60) -> None:
    started = time.time()
    while time.time() - started < timeout_seconds:
        try:
            with socket.create_connection((host, port), timeout=2):
                return
        except OSError:
            time.sleep(1)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")


def wait_for_mongo(uri: str) -> None:
    started = time.time()
    while time.time() - started < 60:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")
            return
        except Exception:
            time.sleep(1)
    raise TimeoutError("Timed out waiting for MongoDB")


if __name__ == "__main__":
    try:
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
        minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        minio_host, minio_port = minio_endpoint.split(":")

        wait_for_mongo(mongo_uri)
        wait_for_port(minio_host, int(minio_port))
        print("All dependent services are reachable.")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
