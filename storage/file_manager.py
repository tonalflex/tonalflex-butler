# storage/file_manager.py
import os
import json

def save_json(directory, name, data):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as f:
        f.write(data)

def load_json(directory, name):
    path = os.path.join(directory, f"{name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return None

def list_sessions(directory):
    if not os.path.exists(directory):
        return []
    return [f[:-5] for f in os.listdir(directory) if f.endswith(".json")]

def delete_file(directory, name):
    path = os.path.join(directory, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
        return True, "Deleted"
    return False, "File not found"
