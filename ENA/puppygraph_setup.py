import requests
import time

API = "http://localhost:8081"


def wait():
    for _ in range(10):
        try:
            requests.get(API)
            return
        except:
            time.sleep(2)


def setup():
    # Catalog
    requests.post(f"{API}/api/catalog", json={
        "name": "ena_graph",
        "datasource": {
            "type": "postgresql",
            "host": "postgres",
            "port": 5432,
            "database": "ena_db",
            "user": "postgres",
            "password": "postgres123"
        }
    })

    # Schema
    requests.post(f"{API}/api/schema", json={
        "catalog": "ena_graph",
        "nodes": [
            {
                "label": "Sample",
                "table": "samples",
                "id": "id"
            }
        ]
    })

    print("✅ PuppyGraph ready")


if __name__ == "__main__":
    wait()
    setup()