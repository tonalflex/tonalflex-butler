#!/bin/bash
set -euo pipefail

echo "[generate-proto] 🔧 Installing dependencies system-wide..."
pip install -r requirements.txt

echo "[generate-proto] 👷 Generating Protobuf files..."
python3 utils/compile_proto.py

echo "[generate-proto] ✅ Protobuf files generated successfully!"
