import sys
import subprocess
import tempfile
import shutil
import platform
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import os

# -----------------------------
# Configuration
# -----------------------------
FQBN = "rp2040:rp2040:rpipico"
ThirdPartyCodeURL = "https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json"
SKETCH_NAME = os.path.join(os.path.dirname(__file__),"main.ino") 
ARDUINO_CLI = os.path.join(os.path.dirname(__file__), "arduino-cli.exe" if platform.system()=="Windows" else "arduino-cli")
# -----------------------------
# Helper functions
# -----------------------------
def list_rp2040_ports(log_widget):
    """Return a list of ports with RP2040 or Pico boards detected."""
    ports = []

    try:
        insert_log(log_widget, "🔍 Scanning for available ports...")
        result = subprocess.check_output([ARDUINO_CLI, "board", "list"], creationflags = subprocess.CREATE_NO_WINDOW).decode()
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
        messagebox.showerror("Error", f"Sketch not found: {SKETCH_NAME}")
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
        log_widget.see(tk.END)
        subprocess.run([ARDUINO_CLI, "compile", "--fqbn", FQBN, str(temp_dir)], creationflags = subprocess.CREATE_NO_WINDOW,
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Upload
        insert_log(log_widget, f"🚀 Uploading to {port}...")
        subprocess.run([ARDUINO_CLI, "upload", "-p", port, "--fqbn", FQBN, str(temp_dir)], creationflags = subprocess.CREATE_NO_WINDOW,
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        insert_log(log_widget, "✅ Upload complete! You may unplug your board now.")
    except subprocess.CalledProcessError as e:
        insert_log(log_widget, f"❌ Error during process:\n{e.output.decode(errors='ignore')}")
        messagebox.showerror("Flashing Error", f"An error occurred during flashing to port {port}. Check the dialog box for details.")
    except Exception as e:
        insert_log(log_widget, f"❌ Unexpected error: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def insert_log(log_widget, message):
    log_widget.insert(tk.END, message + "\n")
    log_widget.update_idletasks()
    log_widget.see(tk.END)

def on_flash_click():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    port = port_var.get().strip()

    if not username or not password:
        messagebox.showwarning("Input required", "Please enter both username and password.")
        return

    if not port:
        messagebox.showwarning("Port required", "Please select a COM port.")
        return

    flash_board(username, password, port, log_box)

def on_refresh_click():
    refresh_ports(log_box)

def refresh_ports(log_widget):
    ports = list_rp2040_ports(log_widget)
    port_menu["values"] = ports
    if ports:
        port_var.set(ports[0])
    else:
        port_var.set("")

def check_dependencies(log_widget):
    try:
        insert_log(log_widget, "🔍 Checking for required cores...")
        core = ':'.join(FQBN.split(":")[:2])
        result = subprocess.check_output([ARDUINO_CLI, "core", "list"],  creationflags = subprocess.CREATE_NO_WINDOW).decode()
        if core not in result:
            if (messagebox.askokcancel("Core Installation", f"{core} needs to be installed. Proceed?")):
                insert_log(log_widget, f"⬇️ Installing {core} core...")
                subprocess.run([ARDUINO_CLI, "config", "add", "board_manager.additional_urls", ThirdPartyCodeURL], creationflags = subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                subprocess.run([ARDUINO_CLI, "core", "update-index"], creationflags = subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                subprocess.run([ARDUINO_CLI, "core", "install", core], creationflags = subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                insert_log(log_widget, f"✅ {core} core installed.")
                messagebox.showinfo("Core Installation", f"{core} core installed.")
            else:
                sys.exit(0)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Dependency Error", f"Failed to verify/install {core} core: {e}")
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("Dependency Error", f"Failed to verify/install {core} core: {e}")
        sys.exit(1)

# -----------------------------
# GUI Setup
# -----------------------------
root = tk.Tk()

# Set window icon
if platform.system()=="Windows":
    icon_path = os.path.join(os.path.dirname(__file__), "password-keyboard.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
else:
    icon_path = os.path.join(os.path.dirname(__file__), "password-keyboard.png")
    if os.path.exists(icon_path):
        icon_img = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon_img)

root.title("Password Keyboard Flasher")
root.geometry("520x440")
root.resizable(False, False)

# Username
username_frame = tk.Frame(root)
username_frame.pack(anchor="w", padx=10, pady=(10, 0))

tk.Label(username_frame, text="Username:").pack(side="left")
username_entry = tk.Entry(username_frame, width=40)
username_entry.pack(side="left")

# Password
password_frame = tk.Frame(root)
password_frame.pack(anchor="w", padx=10, pady=(10, 0))

tk.Label(password_frame, text="Password:").pack(side="left")
password_entry = tk.Entry(password_frame, width=40, show="*")
password_entry.pack(side="left")

# COM Port selector
port_frame = tk.Frame(root)
port_frame.pack(fill="x", padx=10, pady=(10, 0))
tk.Label(port_frame, text="Select Port:").pack(side="left")

port_var = tk.StringVar()
port_menu = ttk.Combobox(port_frame, textvariable=port_var, width=30, state="readonly")
port_menu.pack(side="left", padx=5)

refresh_button = tk.Button(port_frame, text="↻ Refresh", command=on_refresh_click)
refresh_button.pack(side="left", padx=5)

# Flash button
flash_button = tk.Button(root, text="Flash to RP2040", command=on_flash_click,
                         bg="#4CAF50", fg="white", height=2)
flash_button.pack(pady=10, padx=10, fill="x")

# Log box
log_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12)
log_box.pack(padx=10, pady=10, fill="both", expand=True)

# Make sure rp2040 core is available
check_dependencies(log_box)

# Load ports initially
refresh_ports(log_box)

root.mainloop()
