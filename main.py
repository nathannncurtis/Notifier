import os
import json
import threading
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QFrame, QListWidget, QListWidgetItem, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import monitor  #.py

CONFIG_FILE = "config.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Folder Monitor")
        self.setFixedSize(400, 300)

        icon_path = os.path.join(BASE_DIR, 'notif.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.dark_mode = False
        self.init_ui()
        self.load_and_monitor_folders()

    def closeEvent(self, event):
        """Override the close event to hide the window instead of closing."""
        event.ignore()  # Ignore the close event
        self.hide()     # Send to system tray instead of closing

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # Title 
        title_label = QLabel("Folder Monitor")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        # Frame 
        content_frame = QFrame()
        content_layout = QVBoxLayout()

        # List 
        self.folder_list = QListWidget()
        
        # Button to add folders
        self.select_folder_btn = QPushButton("Add Folder")
        self.select_folder_btn.setFont(QFont("Arial", 10))
        self.select_folder_btn.clicked.connect(self.choose_folder)
        
        # Toggle Theme Button
        self.toggle_mode_btn = QPushButton("Toggle Theme")
        self.toggle_mode_btn.setFont(QFont("Arial", 10))
        self.toggle_mode_btn.clicked.connect(self.toggle_mode)

        # Add elements 
        content_layout.addWidget(self.folder_list)
        content_layout.addWidget(self.select_folder_btn)
        content_layout.addWidget(self.toggle_mode_btn)
        
        content_frame.setLayout(content_layout)
        content_frame.setFrameShape(QFrame.StyledPanel)
        
        # Add title and frame to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)

        # Initialize default (dark) mode
        self.apply_dark_mode()

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            child_name = os.path.basename(folder)
            item = QListWidgetItem(child_name)  
            self.folder_list.addItem(item)

            # Start monitoring folder for new thread
            threading.Thread(
                target=monitor.monitor_folder,
                args=(folder, lambda path, folder=folder: monitor.notify(path, folder)),
                daemon=True  # Run as a daemon
            ).start()
            self.update_config_file(folder, child_name)

    def update_config_file(self, full_path, child_name):
        """Update config.json to store full paths and child-most names."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        else:
            config = {"folders": [], "child_names": []}

        if full_path not in config["folders"]:
            config["folders"].append(full_path)
            config["child_names"].append(child_name)

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def load_and_monitor_folders(self):
        """Load folders from config.json and start monitoring each if they exist."""
        if not os.path.exists(CONFIG_FILE) or os.path.getsize(CONFIG_FILE) == 0:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"folders": [], "child_names": []}, f)

        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            folders = config.get("folders", [])
            child_names = config.get("child_names", [])

            for full_path, child_name in zip(folders, child_names):
                if os.path.exists(full_path):  # Check if exits
                    item = QListWidgetItem(child_name)
                    self.folder_list.addItem(item)

                    # Start a thread 
                    threading.Thread(
                        target=monitor.monitor_folder,
                        args=(full_path, lambda path, folder=full_path: monitor.notify(path, folder)),
                        daemon=True  # Run as a daemon
                    ).start()

    def toggle_mode(self):
        if self.dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()
        self.dark_mode = not self.dark_mode

    def apply_dark_mode(self):      # Dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                font-size: 14px;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QListWidget {
                background-color: #3e3e3e;
                color: white;
                padding: 8px;
                font-size: 13px;
                border: 1px solid #4a90e2;
                border-radius: 4px;
            }
        """)

    def apply_light_mode(self):     # Light Theme
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #2e2e2e;
                font-size: 14px;
            }
            QPushButton {
                background-color: #357ABD;
                color: white;
                font-size: 14px;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a90e2;
            }
            QListWidget {
                background-color: #ffffff;
                color: #2e2e2e;
                padding: 8px;
                font-size: 13px;
                border: 1px solid #357ABD;
                border-radius: 4px;
            }
        """)

def setup_tray_icon(app, window):
    tray_icon = QSystemTrayIcon(QIcon("notif.ico"), app)
    tray_menu = QMenu()

    # Show 
    show_action = QAction("Show Window", window)
    show_action.triggered.connect(window.show)
    tray_menu.addAction(show_action)

    # Shut Down
    exit_action = QAction("Shut Down", window)
    exit_action.triggered.connect(app.quit)
    tray_menu.addAction(exit_action)

    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

def main():
    app = QApplication(sys.argv)
    window = ConfigWindow()
    setup_tray_icon(app, window)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
