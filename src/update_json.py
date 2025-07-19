import json
import os
import fcntl
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, '..', 'data.json')


def update_sensor_data(sensor_key, data_dict):
    with open(JSON_PATH, 'a+', encoding='utf-8') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        try:
            content = f.read()
            all_data = json.loads(content) if content else {}
        except json.JSONDecodeError:
            all_data = {}

        all_data[sensor_key] = {
            'timestamp': datetime.now().isoformat(),
            'data': data_dict
        }

        f.seek(0)
        f.truncate()
        json.dump(all_data, f)
