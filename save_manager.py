import json
import os
from constants import SAVE_PATH


class SaveManager:
    @staticmethod
    def load():
        default_data = {
            "unlocked": {"1": 1, "2": 0},
            "keep_progress": True,
            "settings": {"music_volume": 0.1, "sfx_volume": 1.0},
        }
        if not os.path.exists(SAVE_PATH):
            return default_data
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "unlocked" not in data:
                    data["unlocked"] = {}
                data["unlocked"].setdefault("1", 1)
                data["unlocked"].setdefault("2", 0)
                settings = data.setdefault("settings", {})
                settings.setdefault("music_volume", 0.1)
                settings.setdefault("sfx_volume", 1.0)
                return data
        except Exception:
            return default_data

    @staticmethod
    def save(data):
        try:
            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Save failed: {e}")
