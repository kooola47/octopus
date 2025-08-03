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

# No changes needed in this file for renaming taskmanager to dbhelper.
# Just ensure you update all imports in your project from:
# from taskmanager import ...
# to:
# from dbhelper import ...
