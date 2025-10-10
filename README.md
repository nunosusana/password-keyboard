# Password keyboard

**This project bundles Arduino CLI and makes use of the official RP2040 core.**

## Purpose

Turns a RP Pico or another board that uses the RP2040 mirocontroller into a simple macro keyboard that will send key strokes to fill a username and password prompt. This action will occur on every boot.

## Requirements
- Python 3
- Python Tkinter

It is not needed to have installed arduino-cli since this project is bundled with the necessary libraries.

## Possible issues
This project should run on both Linux and Windows, but is was only tested on Linux environments.

## Build

```bash
pip install pyinstaller
```

### Linux
```bash
pyinstaller --onefile --noconsole --add-data "main.ino:." --add-binary "arduino-cli:." --icon "password-keyboard.ico" flasher.py 
```

### Windows
```bash
pyinstaller.exe --onefile --noconsole --add-data "main.ino;." --add-binary "arduino-cli.exe;." --name "password-keyboard" --icon "password-keyboard.ico" --version-file version.txt flasher.py
```

## Run
```bash
python3 flasher.py
```

