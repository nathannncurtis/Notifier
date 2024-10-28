import os
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification

CONFIG_FILE = "config.json"

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, notify_callback, monitored_folder):
        super().__init__()
        self.notify_callback = notify_callback
        self.monitored_folder = monitored_folder  

    def on_created(self, event):
        if not event.is_directory:
            print(f"Detected new file: {event.src_path}")  # Debug
            self.notify_callback(event.src_path, self.monitored_folder)  # Pass
def notify(file_path, monitored_folder):
    """
    Displays a notification for file events.
    
    :param file_path: Path of the file triggering the event.
    :param monitored_folder: Path of the folder being monitored.
    """
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    folder_name = os.path.basename(monitored_folder)
    title = "Please resave the records"
    message = f"{file_name} in {folder_name}"
    
    print(f"Showing notification: {title} - {message}")  # Debug
    notification.notify(
        title=title,
        message=message,
        app_icon="notif.ico",  
        timeout=15
    )

def monitor_folder(path, notify_callback):
    event_handler = FileEventHandler(notify_callback, path)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    print(f"Started monitoring folder: {path}")  # Debug

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def load_folder_path():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            print("Loaded folder path from config:", config.get("folder_path"))  # Debug
            return config.get("folder_path")
    except (FileNotFoundError, json.JSONDecodeError):
        print("Config file not found or invalid.")
        return None
