import random
from typing import List
from storage.user_storage import UserStorage
from config import DIRS


class NicknameService:
    def __init__(self):
        self.user_storage = UserStorage()
        
        self.first_words = [
            "Silent", "Dark", "Neon", "Shadow", "Phantom", "Ghost", "Void", "Eclipse", "Night", "Black",
            "Cryptic", "Mystic", "Spectral", "Twilight", "Obsidian", "Luminous", "Whisper", "Arcane", "Celestial", "Infinite",
            "Abyss", "Pulse", "Mirage", "Wraith", "Flux", "Glimmer", "Shroud", "Beacon", "Glitch", "Silhouette",
            "Veil", "Dusk", "Trace", "Cipher", "Flux", "Nova", "Prism", "Quantum", "Rift", "Rune",
            "Serene", "Storm", "Surge", "Tempest", "Vortex", "Warp", "Zenith", "Aurora", "Blaze", "Cinder",
            "Ember", "Frost", "Gale", "Haze", "Inferno", "Lurker", "Nexus", "Oracle", "Phantom", "Pulse",
            "Quasar", "Rift", "Signal", "Specter", "Surge", "Twilight", "Umbra", "Vesper", "Void", "Zenith",
            "Aether", "Arc", "Ash", "Aurora", "Blackout", "Blaze", "Blink", "Chasm", "Comet", "Cosmos",
            "Echo", "Ember", "Flux", "Frost", "Glint", "Halo", "Horizon", "Ignite", "Ion", "Lumen",
            "Mist", "Nebula", "Nexus", "Nova", "Oculus", "Phantom", "Pulse", "Quasar", "Rift", "Sable"
        ]
        
        self.second_words = [
            "Echo", "Wraith", "Cipher", "Flux", "Glimmer", "Shroud", "Beacon", "Glitch", "Silhouette", "Veil",
            "Dusk", "Trace", "Phantom", "Pulse", "Rift", "Rune", "Shadow", "Specter", "Surge", "Twilight",
            "Umbra", "Vesper", "Void", "Zenith", "Aether", "Arc", "Ash", "Aurora", "Blackout", "Blaze",
            "Blink", "Chasm", "Comet", "Cosmos", "Echo", "Ember", "Flux", "Frost", "Glint", "Halo",
            "Horizon", "Ignite", "Ion", "Lumen", "Mist", "Nebula", "Nexus", "Nova", "Oculus", "Phantom",
            "Pulse", "Quasar", "Rift", "Sable", "Shade", "Shift", "Shiver", "Signal", "Silk", "Sky",
            "Slash", "Smog", "Smoke", "Sonic", "Soul", "Spark", "Spectral", "Spire", "Starlight", "Static",
            "Stealth", "Storm", "Surge", "Synth", "Tempest", "Thunder", "Tide", "Token", "Trace", "Twilight",
            "Veil", "Vapor", "Vector", "Velvet", "Verge", "Vibe", "Vortex", "Wand", "Warp", "Wave",
            "Whisper", "Wisp", "Zenith", "Zero", "Zone", "Zypher", "Abyss", "Arcane", "Blaze", "Cipher"
        ]
    
    def is_nickname_used(self, nickname: str) -> bool:
        return self.user_storage.find_by_username(nickname) is not None
    
    def generate_nickname(self) -> str:
        while True:
            first = random.choice(self.first_words)
            second = random.choice(self.second_words)
            nickname = f"{first} {second}"
            if first != second and not self.is_nickname_used(nickname):
                break
        return nickname