from crypto import Crypto
import json
import os
import secrets
from datetime import datetime
import random

class Core:
    def __init__(self):
        self.crypto = Crypto()
    
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
    
    def if_nickname_used(self, nickname):
        if not os.path.exists('data/users'):
            return False
    
        user_files = [f for f in os.listdir('data/users') if f.endswith('.json')]
    
        for filename in user_files:
            filepath = f'data/users/{filename}'
            try:
                with open(filepath, 'r') as f:
                    user_data = json.load(f)
                if user_data.get('username') == nickname:
                    return True
            except:
                continue
        return False

    def generate_nickname(self):
        while True:
            first = random.choice(self.first_words)
            second = random.choice(self.second_words)
            nickname = f"{first} {second}"
            if first != second and self.if_nickname_used(nickname) == False:
                break
                
        return nickname

    def register(self):
        user_id = secrets.token_hex(4).upper()
        seed_phrase = self.crypto.generate_seed_phrase()
        username = self.generate_nickname()

        user_data = {
            "user_id": user_id,
            "username": username,
            "seed_phrase": seed_phrase,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        os.makedirs('data/users', exist_ok=True)
        filename = f'data/users/user_{user_id}.json'
        with open(filename, 'w') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)
        
        return {
            'user_id': user_id,
            'seed_phrase': seed_phrase,
            'username': user_data['username']
        }
    
    def login(self, seed_phrase):
        if not os.path.exists('data/users'):
            return None
        
        user_files = [f for f in os.listdir('data/users') if f.endswith('.json')]
        
        for filename in user_files:
            filepath = f'data/users/{filename}'
            try:
                with open(filepath, 'r') as f:
                    user_data = json.load(f)
                if user_data.get('seed_phrase') == seed_phrase:
                    return user_data
            except:
                continue
        
        return None