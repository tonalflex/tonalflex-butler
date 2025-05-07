# storage/file_manager.py
import os
import json

# --- JSON file helpers (used for sessions) non binary ---

def list_sessions(directory):
    if not os.path.exists(directory):
        return []
    return sorted(f[:-5] for f in os.listdir(directory) if f.endswith(".json"))

def save_session(directory, name, data):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)

def load_session(directory, name):
    path = os.path.join(directory, f"{name}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def delete_session(directory, name):
    path = os.path.join(directory, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
        return True, "Session deleted"
    return False, "File not found"

def rename_session(directory, old_name, new_name):
    old_path = os.path.join(directory, f"{old_name}.json")
    new_path = os.path.join(directory, f"{new_name}.json")
    if not os.path.exists(old_path):
        return False, "Session not found"
    if os.path.exists(new_path):
        return False, "Target session name already exists"
    os.rename(old_path, new_path)
    return True, "Renamed successfully"

# --- Generic file helpers (used for NAM, IR, etc.) binary ---

def list_files(directory):
    if not os.path.exists(directory):
        return []
    return sorted(f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)))

def save_file(directory, filename, content_bytes):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, "wb") as f:
        f.write(content_bytes)

def read_file(directory, filename):
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()

def delete_file(directory, filename):
    path = os.path.join(directory, filename)
    if os.path.exists(path):
        os.remove(path)
        return True, "Deleted"
    return False, "File not found"

def rename_file(directory, old_name, new_name):
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)
    if not os.path.exists(old_path):
        return False, "Source file not found"
    if os.path.exists(new_path):
        return False, "Target file already exists"
    os.rename(old_path, new_path)
    return True, "Renamed successfully"
