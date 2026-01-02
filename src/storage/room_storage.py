from pathlib import Path
from typing import Dict, List, Any
from storage.base import FileStorage
from config import DIRS


class RoomStorage:
    def __init__(self):
        self.user_file_storage = FileStorage(DIRS["user_rooms"])
        self.global_file_storage = FileStorage(DIRS["data"])
    
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