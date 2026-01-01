import hashlib
import secrets

class Crypto:
    def __init__(self, dictionary_path='data/bip39.txt'):
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            self.dictionary = [line.strip() for line in f if line.strip()]
    
    def generate_seed_phrase(self):
        entropy_bytes = secrets.token_bytes(16)
        hash_bytes = hashlib.sha256(entropy_bytes).digest()
        checksum = bin(int.from_bytes(hash_bytes, 'big'))[2:].zfill(256)[:4]
        entropy_bin = bin(int.from_bytes(entropy_bytes, 'big'))[2:].zfill(128)
        bits = entropy_bin + checksum
        chunks = [bits[i:i+11] for i in range(0, 132, 11)]
        seed_phrase = " ".join(self.dictionary[int(chunk, 2)] for chunk in chunks)
        return seed_phrase

    def hash_seed_phrase(self, seed_phrase):
        hash_bytes = hashlib.sha256(seed_phrase.encode()).digest()
        return hash_bytes.hex()