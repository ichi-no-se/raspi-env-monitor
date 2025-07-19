import json
import os
import fcntl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, '..', 'data.json')


def read_sensor_data():
    if not os.path.exists(JSON_PATH):
        return {}
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            content = f.read()
            return json.loads(content) if content else {}
        except json.JSONDecodeError:
            return {}