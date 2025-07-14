import threading
import time

class Scheduler:
    def __init__(self):
        self.tasks = []

    def add_task(self, func, interval):
        def wrapper():
            while True:
                func()
                time.sleep(interval)
        t = threading.Thread(target=wrapper, daemon=True)
        t.start()
        self.tasks.append(t)
