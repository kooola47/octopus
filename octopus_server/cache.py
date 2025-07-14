import time

class Cache:
    def __init__(self):
        self.data = {}

    def set(self, key, value, ttl=None):
        self.data[key] = (value, time.time() + ttl if ttl else None)

    def get(self, key):
        value, expire = self.data.get(key, (None, None))
        if expire and expire < time.time():
            del self.data[key]
            return None
        return value

    def all(self):
        return {k: v[0] for k, v in self.data.items() if not v[1] or v[1] > time.time()}
