from pathlib import Path
from typing import Dict, List, Any
from storage.base import FileStorage
from config import DIRS
from datetime import datetime

class RoomStorage:
    def __init__(self):
        self.user_file_storage = FileStorage(DIRS["user_rooms"])
        self.global_file_storage = FileStorage(DIRS["data"])
        self.rooms_file_storage = FileStorage(DIRS["rooms_management"])
    
    def load_user_rooms(self, user_id: str) -> List[str]:
        filename = f"{user_id}.json"
        data = self.user_file_storage.load(filename)
        return data if data else ["general"]
    
    def save_user_rooms(self, user_id: str, rooms: List[str]) -> None:
        filename = f"{user_id}.json"
        self.user_file_storage.save(filename, rooms)
    
    def load_global_chat_rooms(self) -> Dict[str, List[Dict[str, Any]]]:
        return self.global_file_storage.load("global_chat_rooms.json")
    
    def save_global_chat_rooms(self, chat_rooms: Dict[str, List[Dict[str, Any]]]) -> None:
        self.global_file_storage.save("global_chat_rooms.json", chat_rooms)

    def load_global_room_names(self) -> List[str]:
        names = self.global_file_storage.load("global_room_names.json")
        if not names:
            return ["general"]
        if "general" not in names:
            names.insert(0, "general")
        return names

    def save_global_room_names(self, names: List[str]) -> None:
        names_set = set(names)
        names_set.add("general")
        final = ["general"] + [r for r in names if r != "general"]
        self.global_file_storage.save("global_room_names.json", final)

    def room_exists(self, room_name: str) -> bool:
        return self.rooms_file_storage.exists(f"{room_name}.json")

    def get_room_meta(self, room_name: str) -> dict:
        return self.rooms_file_storage.load(f"{room_name}.json")

    def create_room(self, room_name: str, creator: str, secure: str = "public", password: str = None) -> dict:
        room_meta = {
            "creator": creator,
            "created": datetime.now().isoformat(),
            "secure": secure,
            "password": password
        }
        self.rooms_file_storage.save(f"{room_name}.json", room_meta)
        return room_meta

    def get_all_user_rooms(self) -> List[str]:
        return [f.stem for f in DIRS["rooms_management"].glob("*.json")]
