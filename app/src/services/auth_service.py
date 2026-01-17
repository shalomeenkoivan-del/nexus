import secrets
from datetime import datetime
from models.user import User
from services.crypto import Crypto
from services.nickname_service import NicknameService
from storage.user_storage import UserStorage

class AuthService:
    def __init__(self):
        self.crypto = Crypto()
        self.nickname = NicknameService()
        self.storage = UserStorage()
    
    def register(self) -> dict:
        user_id = secrets.token_hex(4).upper()
        seed_phrase = self.crypto.generate_seed_phrase()
        username = self.nickname.generate_nickname()

        user = User(
            user_id=user_id,
            username=username,
            seed_phrase=seed_phrase
        )
        
        self.storage.save_user(user)
        
        return {
            'user_id': user_id,
            'seed_phrase': seed_phrase,
            'username': username
        }
    
    def login(self, seed_phrase: str) -> User:
        return self.storage.find_by_seed(seed_phrase)