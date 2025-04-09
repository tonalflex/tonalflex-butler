#!/bin/bash
set -euo pipefail

echo "[build] 🔧 Installing system build dependencies..."
apt-get update && apt-get install -y --no-install-recommends \
  build-essential gcc curl git \
  && rm -rf /var/lib/apt/lists/*

echo "[build] 🔧 Installing Python build deps..."
pip install --upgrade pip
pip install pyinstaller
pip install -r requirements.txt

echo "[build] 👷 Building binary..."
pyinstaller --onefile server/main.py --name butler

echo "[build] ✅ Binary available at: dist/butler"