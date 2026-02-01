import json
import time

import requests
import os

dirs = os.listdir("output_batches")
for dir in dirs:
    if dir.endswith(".json"):
        with open(f"output_batches/{dir}", "r") as file:
            data = json.load(file)

        resp = requests.post("http://localhost:8080/ingest", json=data)

        resp.raise_for_status()
        print("Status code: ",resp.status_code)
        print("Response: ",resp.json())
    time.sleep(2)