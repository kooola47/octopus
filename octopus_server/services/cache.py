import time
import threading

class Cache:
    def __init__(self):
        self.data = {}
        self.lock = threading.RLock()  # Reentrant lock for thread safety

    def set(self, key, value, ttl=None):
        with self.lock:
            self.data[key] = (value, time.time() + ttl if ttl else None)

    def get(self, key):
        with self.lock:
            value, expire = self.data.get(key, (None, None))
            if expire and expire < time.time():
                del self.data[key]
                return None
            return value

    def all(self):
        with self.lock:
            current_time = time.time()
            # Clean expired entries while we're at it
            expired_keys = [k for k, (v, exp) in self.data.items() if exp and exp < current_time]
            for key in expired_keys:
                del self.data[key]
            
            return {k: v[0] for k, v in self.data.items() if not v[1] or v[1] > current_time}
    
    def delete(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
    
    def clear(self):
        with self.lock:
            self.data.clear()
    
    def size(self):
        with self.lock:
            return len(self.data)
