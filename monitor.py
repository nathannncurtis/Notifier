import os
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from win10toast import ToastNotifier

CONFIG_FILE = "config.json"

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, notify_callback):
        super().__init__()
        self.notify_callback = notify_callback

    def on_created(self, event):
        if not event.is_directory:
            print(f"Detected new file: {event.src_path}")  # Debugger
            self.notify_callback(event.src_path)

def monitor_folder(path, notify_callback):
    event_handler = FileEventHandler(notify_callback)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    print(f"Started monitoring folder: {path}")  # Debugger

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
            print("Loaded folder path from config:", config.get("folder_path"))  # Debugger
            return config.get("folder_path")
    except (FileNotFoundError, json.JSONDecodeError):
        print("Config file not found or invalid.")
        return None

if __name__ == "__main__":
    toaster = ToastNotifier()

toaster = ToastNotifier()
ICON_PATH = "your_icon.ico" 

def notify(event_type, file_path):
    """
    Displays a notification for file events.
    
    :param event_type: Type of event (e.g., "File Added").
    :param file_path: Path of the file triggering the event.
    """
    file_name = os.path.basename(file_path)
    title = f"My Custom App - {event_type}"
    message = f"{file_name} has been {event_type.lower()}."
    
    print(f"Showing notification: {title} - {message}")  # Debugger
    toaster.show_toast(
        title,
        message,
        icon_path=ICON_PATH if os.path.exists(ICON_PATH) else None,
        duration=5
    )

folder_path = load_folder_path()
if folder_path:
    monitor_folder(folder_path, lambda path: notify("File Added", path))
else:
    print("No folder configured. Run ui_config.py to set the folder path.")
