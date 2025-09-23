import json
from pathlib import Path
from threading import Lock

class Cache:
    def __init__(self, filename='cache.json'):
        self.file = Path(filename)
        self.lock = Lock()
        if not self.file.exists():
            self._write({})

    def _read(self):
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write(self, data):
        with self.lock:
            with open(self.file, "w") as f:
                json.dump(data, f, indent=2)

    def set(self, category, key, value):
        data = self._read()
        if category not in data:
            data[category] = {}
        data[category][key] = value
        self._write(data)

    def get(self, category, key, default=None):
        data = self._read()
        return data.get(category, {}).get(key, default)

    def exists(self, category, key):
        data = self._read()
        return key in data.get(category, {})

    def delete(self, category, key):
        data = self._read()
        if key in data.get(category, {}):
            del data[category][key]
            self._write(data)

# Singleton instance
cache = Cache()