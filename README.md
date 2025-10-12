# Password keyboard

**This project bundles Arduino CLI and makes use of the official RP2040 core.**

## Purpose

Turns a RP Pico or another board that uses the RP2040 mirocontroller into a simple macro keyboard that will send key strokes to fill a username and password prompt. This action will occur on every boot.

## Contribute

### Requirements
- Python 3
- Python Tkinter - for Tkinter version
- PyQt - for Qt version
```bash
pip install PyQt5
```

It is not needed to have installed arduino-cli since this project is bundled with the necessary libraries.

### Building the executable

```bash
pip install pyinstaller
```

#### Linux
- Tkinter version
```bash
pyinstaller --onefile --noconsole --add-data "main.ino:." --add-data "password-keyboard.png:." --add-binary "arduino-cli:." --name "password-keyboard" flasher.py 
```
- Qt version
```bash
pyinstaller --onefile --noconsole --add-data "main.ino:." --add-data "password-keyboard.png:." --add-binary "arduino-cli:." --name "password-keyboard" flasher-qt.py 
```

#### Windows
- Tkinter version
```bash
pyinstaller.exe --onefile --noconsole --add-data "main.ino;." --add-data "password-keyboard.ico;." --add-binary "arduino-cli.exe;." --name "password-keyboard" --icon "password-keyboard.ico" --version-file version.txt flasher.py
```
- Qt version
```bash
pyinstaller.exe --onefile --noconsole --add-data "main.ino;." --add-data "password-keyboard.ico;." --add-binary "arduino-cli.exe;." --name "password-keyboard" --icon "password-keyboard.ico" --version-file version.txt flasher-qt.py
```

