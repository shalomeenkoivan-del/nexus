import json
from pathlib import Path
from typing import Any, Dict, List

class FileStorage:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        if self.base_path.is_file():
            self.base_path = self.base_path.parent
    
    def load(self, filename: str) -> Dict[str, Any]:
        filepath = self.base_path / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save(self, filename: str, data: Any) -> None:
        filepath = self.base_path / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def list_files(self, pattern: str = "*.json") -> List[str]:
        if not self.base_path.exists():
            return []
        return [f for f in self.base_path.glob(pattern) if f.is_file()]

    def exists(self, filename):
        filepath = self.base_path / filename
        return filepath.exists()