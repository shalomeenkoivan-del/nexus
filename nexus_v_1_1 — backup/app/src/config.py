import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"

DIRS = {
    "data": DATA_DIR,
    "users": DATA_DIR / "users",
    "user_rooms": DATA_DIR / "user_rooms",
    "images": DATA_DIR / "images",
    "global_chat_rooms": DATA_DIR / "global_chat_rooms.json",
    "bip39": DATA_DIR / "bip39.txt",
    "templates": TEMPLATES_DIR
}

for path in DIRS.values():
    if isinstance(path, Path) and path.is_dir():
        path.mkdir(parents=True, exist_ok=True)