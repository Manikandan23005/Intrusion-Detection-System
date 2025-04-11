# monitor.py

import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from alert import send_email
from client_api import add_log
import json
uid=0
with open('config.json') as file:
    data = json.load(file)
    uid=(data['user_id'])

class IntrusionHandler(FileSystemEventHandler):
    def __init__(self):
        self.recent_events = {}

    def should_ignore(self, path):
        # Ignore temporary/editor files
        return any(path.endswith(ext) for ext in ['.swp', '.tmp', '~'])

    def should_alert(self, path):
        now = time.time()
        last_time = self.recent_events.get(path, 0)
        if now - last_time > 10:  # 10-second debounce per file
            self.recent_events[path] = now
            return True
        return False

    def on_modified(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            if self.should_alert(event.src_path):
                print(f"[DEBUG] Modified: {event.src_path}")
             #   send_email("Intrusion Detected!", f"A file was modified: {event.src_path}")
                add_log(uid,"File Mofification","Unknown",f"User Modifies a file : {event.src_path}","low")
    def on_created(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            if self.should_alert(event.src_path):
                print(f"[DEBUG] Created: {event.src_path}")
             #  send_email("Intrusion Detected!", f"A new file was created: {event.src_path}")
                add_log(2727,"File Mofification","Unknown",f"A new file was created: {event.src_path}","low")

class IntrusionMonitor:
    def __init__(self, path):
        self.event_handler = IntrusionHandler()
        self.observer = Observer()
        self.path = path

    def run(self):
        print(f"[INFO] Monitoring started on {self.path}")
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            print("[INFO] Monitoring stopped by user.")
        self.observer.join()
