from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    user_id: str
    username: str
    seed_phrase: str
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(**{k: data[k] for k in cls.__annotations__ if k in data})