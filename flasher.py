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
def list_rp2040_ports():
    """Return a list of ports with RP2040 or Pico boards detected."""
    ports = []

    try:
        result = subprocess.check_output([ARDUINO_CLI, "board", "list"]).decode()
        for line in result.splitlines():
            parts = line.split()
            if parts and "port" != parts[0].lower().strip() and "no" != parts[0].lower().strip():
                ports.append(parts[0])
    except Exception:
        pass

    # Fallback: common default ports
    if not ports:
        ports = ["No boards found"]
    return ports


def flash_board(username, password, port, log_widget):
    log_widget.delete("1.0", tk.END)
    log_widget.insert(tk.END, "Starting flash process...\n")

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
        log_widget.insert(tk.END, "🛠 Compiling sketch...\n")
        log_widget.see(tk.END)
        subprocess.run([ARDUINO_CLI, "compile", "--fqbn", FQBN, str(temp_dir)],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Upload
        log_widget.insert(tk.END, f"🚀 Uploading to {port}...\n")
        log_widget.see(tk.END)
        subprocess.run([ARDUINO_CLI, "upload", "-p", port, "--fqbn", FQBN, str(temp_dir)],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        log_widget.insert(tk.END, "✅ Upload complete!\n")
        messagebox.showinfo("Success", "Flashing complete!")

    except subprocess.CalledProcessError as e:
        log_widget.insert(tk.END, f"❌ Error:\n{e.output.decode(errors='ignore')}\n")
        messagebox.showerror("Flashing failed", "Check logs for details.")
    except Exception as e:
        log_widget.insert(tk.END, f"❌ Unexpected error: {e}\n")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
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

def refresh_ports():
    ports = list_rp2040_ports()
    port_menu["values"] = ports
    if ports:
        port_var.set(ports[0])
    else:
        port_var.set("")

def check_dependencies():
    try:
        core = ':'.join(FQBN.split(":")[:2])
        result = subprocess.check_output([ARDUINO_CLI, "core", "list"]).decode()
        if core not in result:
            if (messagebox.askokcancel("Installing Core", f"{core} needs to be installed. Proceed?")):
                subprocess.run([ARDUINO_CLI, "config", "add", "board_manager.additional_urls", ThirdPartyCodeURL], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                subprocess.run([ARDUINO_CLI, "core", "update-index"], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                subprocess.run([ARDUINO_CLI, "core", "install", core], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                messagebox.showinfo("✅ Core", f"{core} installed.")
            else:
                exit(0)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Dependency Error", f"❌ Failed to verify/install {core} core: {e}")
        exit(1)
    except Exception as e:
        messagebox.showerror("Dependency Error", f"❌ Failed to verify/install {core} core: {e}")
        exit(1)

# -----------------------------
# GUI Setup
# -----------------------------
root = tk.Tk()
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

refresh_button = tk.Button(port_frame, text="↻ Refresh", command=refresh_ports)
refresh_button.pack(side="left", padx=5)

# Flash button
flash_button = tk.Button(root, text="Flash to RP2040", command=on_flash_click,
                         bg="#4CAF50", fg="white", height=2)
flash_button.pack(pady=10, padx=10, fill="x")

# Log box
log_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12)
log_box.pack(padx=10, pady=10, fill="both", expand=True)

# Make sure rp2040 core is available
check_dependencies()

# Load ports initially
refresh_ports()

root.mainloop()
