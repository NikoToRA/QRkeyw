# QR2Key

Convert QR codes to cryptographic keys and vice versa. This tool provides functionality for generating secure keys and representing them as QR codes.

## Features

- Generate cryptographic keys
- Convert keys to QR codes
- Copy keys to clipboard (Windows only)

## Installation

### Regular Installation

```bash
# Install common dependencies
pip install -r requirements.txt

# On Windows, also install Windows-specific dependencies
pip install -r requirements-win.txt  # Windows only
```

## Building Windows Executables

To build the Windows executables:

1. On Windows, run the appropriate batch file:
   - For 32-bit (x86): `build_win_x86.bat`
   - For 64-bit (x64): `build_win_x64.bat`

2. The executables will be created in the `dist` directory.

## Development

For development, it's recommended to use a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dev dependencies
pip install -r requirements.txt
# On Windows
pip install -r requirements-win.txt
```
