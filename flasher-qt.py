import sys
import os
import platform
import subprocess
import tempfile
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QComboBox, QPushButton,
    QTextEdit, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# -----------------------------
# Configuration
# -----------------------------
FQBN = "rp2040:rp2040:rpipico"
ThirdPartyCodeURL = "https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json"
SKETCH_NAME = os.path.join(os.path.dirname(__file__),"main.ino")
ARDUINO_CLI = os.path.join(os.path.dirname(__file__), "arduino-cli.exe" if platform.system()=="Windows" else "arduino-cli")

def list_rp2040_ports(log_widget):
    """Return a list of ports with RP2040 or Pico boards detected."""
    ports = []

    try:
        insert_log(log_widget, "🔍 Scanning for available ports...")
        result = subprocess.check_output([ARDUINO_CLI, "board", "list"]).decode()
        for line in result.splitlines():
            parts = line.split()
            if parts and "port" != parts[0].lower().strip() and "no" != parts[0].lower().strip():
                ports.append(parts[0])
    except Exception:
        pass

    if not ports:
        ports = ["No boards found"]
    return ports

def flash_board(username, password, port, log_widget):
    insert_log(log_widget, f"Starting flashing process on port {port}...")

    sketch_path = Path(SKETCH_NAME)
    if not sketch_path.exists():
        QMessageBox.critical(None, "Error", f"Sketch not found: {SKETCH_NAME}")
        return
    
    temp_dir = Path(tempfile.mkdtemp(prefix="rp2040_build_"))
    temp_sketch = temp_dir / f"{temp_dir.name}.ino"
    try:
        # Replace placeholders
        code = sketch_path.read_text()
        code = code.replace("{{USERNAME}}", username)
        code = code.replace("{{PASSWORD}}", password)
        temp_sketch.write_text(code)

        # Compile
        insert_log(log_widget, "🛠 Compiling sketch...")
        QApplication.processEvents()
        subprocess.run([ARDUINO_CLI, "compile", "--fqbn", FQBN, str(temp_dir)],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        # Upload
        insert_log(log_widget, f"🚀 Uploading to {port}...")
        QApplication.processEvents()
        subprocess.run([ARDUINO_CLI, "upload", "-p", port, "--fqbn", FQBN, str(temp_dir)],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        insert_log(log_widget, "✅ Upload complete! You may unplug your board now.")
    except subprocess.CalledProcessError as e:
        insert_log(log_widget, f"❌ Error during process:\n{e.output.decode(errors='ignore')}")
        QMessageBox.critical(None, "Flashing Error", f"An error occurred during flashing to port {port}. Check the log for details.")
    except Exception as e:
        insert_log(log_widget, f"❌ Unexpected error: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def insert_log(log_widget, message):
    log_widget.append(message)
    log_widget.moveCursor(log_widget.textCursor().End)
    QApplication.processEvents()

def check_dependencies(log_widget):
    try:
        insert_log(log_widget, "🔍 Checking for required cores...")
        core = ':'.join(FQBN.split(":")[:2])
        result = subprocess.check_output([ARDUINO_CLI, "core", "list"]).decode()
        if core not in result:
            reply = QMessageBox.question(None, "Core Installation", f"{core} needs to be installed. Proceed?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                insert_log(log_widget, f"⬇️ Installing {core} core...")
                subprocess.run([ARDUINO_CLI, "config", "add", "board_manager.additional_urls", ThirdPartyCodeURL], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                subprocess.run([ARDUINO_CLI, "core", "update-index"], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                subprocess.run([ARDUINO_CLI, "core", "install", core], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                insert_log(log_widget, f"✅ {core} core installed.")
                QMessageBox.information(None, "Core Installation", f"{core} core installed.")
            else:
                sys.exit(0)
    except subprocess.CalledProcessError as e:
        QMessageBox.critical(None, "Dependency Error", f"Failed to verify/install {core} core: {e}")
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(None, "Dependency Error", f"Failed to verify/install {core} core: {e}")
        sys.exit(1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Keyboard Flasher")
        self.setFixedSize(520, 440)
        # Set window/taskbar icon
        icon_path = None
        if platform.system() == "Windows":
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "password-keyboard.ico")
            else:
                icon_path = os.path.join(os.path.dirname(__file__), "password-keyboard.ico")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "password-keyboard.png")
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Widgets
        central = QWidget()
        layout = QVBoxLayout()

        # Username
        user_layout = QHBoxLayout()
        user_label = QLabel("Username:")
        self.username_entry = QLineEdit()
        self.username_entry.setFixedWidth(445)
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.username_entry)
        layout.addLayout(user_layout)

        # Password
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setFixedWidth(445)
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.password_entry)
        layout.addLayout(pass_layout)

        # Port selector
        port_layout = QHBoxLayout()
        port_label = QLabel("Select Port:")
        self.port_menu = QComboBox()
        self.port_menu.setFixedWidth(200)
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.clicked.connect(self.on_refresh_click)
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_menu)
        port_layout.addWidget(refresh_btn)
        layout.addLayout(port_layout)

        # Flash button
        flash_btn = QPushButton("Flash to RP2040")
        flash_btn.setStyleSheet("background-color: #4CAF50; color: white; height: 32px;")
        flash_btn.clicked.connect(self.on_flash_click)
        layout.addWidget(flash_btn)

        # Log box
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(180)
        layout.addWidget(self.log_box)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def on_flash_click(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()
        port = self.port_menu.currentText().strip()
        if not username or not password:
            QMessageBox.warning(self, "Input required", "Please enter both username and password.")
            return
        if not port:
            QMessageBox.warning(self, "Port required", "Please select a COM port.")
            return
        flash_board(username, password, port, self.log_box)

    def on_refresh_click(self):
        self.refresh_ports()

    def refresh_ports(self):
        ports = list_rp2040_ports(self.log_box)
        self.port_menu.clear()
        self.port_menu.addItems(ports)
        if ports:
            self.port_menu.setCurrentIndex(0)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # Dependency check and initial port load
    check_dependencies(window.log_box)
    window.refresh_ports()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()