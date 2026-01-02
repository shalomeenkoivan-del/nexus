import secrets
from pathlib import Path
from typing import Optional, List
from models.user import User
from storage.base import FileStorage
from config import DIRS


class UserStorage(FileStorage):
    def __init__(self):
        super().__init__(DIRS["users"])
    
    def save_user(self, user: User) -> None:
        filename = f"user_{user.user_id}.json"
        self.save(filename, {
            "user_id": user.user_id,
            "username": user.username,
            "seed_phrase": user.seed_phrase,
            "timestamp": user.timestamp
        })
    
    def find_by_username(self, username: str) -> Optional[User]:
        for file_path in self.list_files():
            data = self.load(file_path.name)
            if data.get('username') == username:
                return User.from_dict(data)
        return None
    
    def find_by_seed(self, seed_phrase: str) -> Optional[User]:
        for file_path in self.list_files():
            try:
                data = self.load(file_path.name)
                if data.get('seed_phrase') == seed_phrase:
                    return User.from_dict(data)
            except:
                continue
        return None
    
    def total_users(self) -> int:
        return len(self.list_files())