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