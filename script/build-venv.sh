#!/bin/bash
set -euo pipefail

echo "[build-venv] 🔧 Creating local virtual environment..."
python3 -m venv .venv

echo "[build-venv] 🐍 Activating venv and installing dependencies..."
. .venv/bin/activate
pip install --upgrade pip
pip install pyinstaller
pip install -r requirements.txt

echo "[build-venv] 👷 Building binary with PyInstaller..."
pyinstaller --onefile server/main.py --name butler

echo "[build-venv] ✅ Binary available at: dist/butler"

