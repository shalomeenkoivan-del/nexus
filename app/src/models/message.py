from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Message:
    user: str
    user_id: str
    message: str
    time: str
    system: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(**data)