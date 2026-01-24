import json
import os
from constants import SAVE_PATH


class SaveManager:
    @staticmethod
    def load():
        default_data = {"unlocked": {"1": 1, "2": 0}, "keep_progress": True}
        if not os.path.exists(SAVE_PATH):
            return default_data
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "unlocked" not in data:
                    data["unlocked"] = {}
                data["unlocked"].setdefault("1", 1)
                data["unlocked"].setdefault("2", 0)
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
