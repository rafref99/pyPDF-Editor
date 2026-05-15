#!/bin/zsh

set -e

APP_DIR="${0:a:h}"
cd "$APP_DIR"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Python 3 is required but was not found."
    echo "Install Python from https://www.python.org/downloads/ and run this launcher again."
    read -r "?Press Enter to close..."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating local Python environment..."
    "$PYTHON_CMD" -m venv .venv
fi

VENV_PYTHON=".venv/bin/python"

echo "Checking and installing requirements..."
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r requirements.txt

echo "Starting pyPDF Editor..."
"$VENV_PYTHON" main.py
