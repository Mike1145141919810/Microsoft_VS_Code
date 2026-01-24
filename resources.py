import os
import sys
import pygame


def resource_path(rel_path: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)


class ResourceManager:
    def __init__(self):
        self.images = {}
        self.fonts = {}
        self.sounds = {}

    def load_image(self, name, path):
        if name not in self.images:
            try:
                img = pygame.image.load(resource_path(path)).convert_alpha()
                self.images[name] = img
            except Exception as e:
                print(f"Error loading {path}: {e}")
                surf = pygame.Surface((50, 50), pygame.SRCALPHA)
                surf.fill((0, 0, 0, 0))
                self.images[name] = surf
        return self.images[name]

    def get_image(self, name):
        return self.images.get(name)

    def load_sound(self, name, path):
        if name not in self.sounds:
            try:
                snd = pygame.mixer.Sound(resource_path(path))
                snd.set_volume(1.0)
                self.sounds[name] = snd
            except Exception as e:
                print(f"Error loading sound {path}: {e}")
        return self.sounds.get(name)

    def load_assets(self):
        self.load_image("bg_main", "resource/UI/MAINPAGE/main_page_background.jpg")
        self.load_image("bg_game1", "resource/UI/GAMING/gaming.jpg")
        self.load_image("bg_game2", "resource/UI/GAMING/gaming2.jpg")
        self.load_image("bg_credits", "resource/UI/CREDITS/CREDITS1.jpg")
        self.load_image("bg_archive", "resource/UI/ARCHIVE/ARCHIVE 首页.png")
        self.load_image("archive_help_1", "resource/UI/ARCHIVE/ARCHIVE 帮助01.png")
        self.load_image("archive_help_2", "resource/UI/ARCHIVE/ARCHIVE 帮助02.png")
        for i in range(1, 7):
            self.load_image(f"植物page{i}", f"resource/UI/ARCHIVE/植物page{i}.png")
        for i in range(1, 5):
            self.load_image(f"BUGspage{i}", f"resource/UI/ARCHIVE/BUGspage{i}.png")
        self.load_image("bg_pause", "resource/UI/GAMING/suspension.png")
        self.load_image("img_lose", "resource/UI/GAMING/lose.png")
        self.load_image("img_return", "resource/UI/GAMING/return_instruction.png")
        self.load_image("img_win_final", "resource/UI/GAMING/win0.png")
        self.load_image("img_win_normal", "resource/UI/CREDITS/credits.jpg")
        for i in range(2, 6):
            self.load_image(f"credits{i}", f"resource/UI/CREDITS/CREDITS{i}.jpg")

        self.load_sound("bgm", "resource/sounds/bgm.wav")
        self.load_sound("start", "resource/sounds/start.wav")
        self.load_sound("error", "resource/sounds/error.wav")
        self.load_sound("error1", "resource/sounds/error1.wav")
        self.load_sound("set", "resource/sounds/set.wav")
        self.load_sound("remove", "resource/sounds/remove.wav")
        self.load_sound("win", "resource/sounds/win.wav")

        self.load_image("hl_start", "resource/UI/MAINPAGE/main_page_background_start_highlight.jpg")
        self.load_image("hl_save", "resource/UI/MAINPAGE/main_page_background_archive_highlight.jpg")
        self.load_image("hl_quit", "resource/UI/MAINPAGE/main_page_background_quit_highlight.jpg")
        self.load_image("hl_credits", "resource/UI/MAINPAGE/main_page_background_credits_highlight.jpg")
        self.load_image("select_overlay", "resource/UI/CREDITS/CHOOSEIDE1.png")
        self.load_image("level_hover", "resource/UI/CREDITS/BACKGROUND.png")

        self.load_image("cleaner", "resource/aids/cleaner.png")
        self.load_image("hidden", "resource/aids/hidden.png")
        self.load_image("no_money", "resource/aids/no_money.png")

        for i in range(1, 17):
            self.load_image(f"idle_{i}", f"resource/idle_org/idle_{i}.png")
            self.load_image(f"idle_{i}withcost", f"resource/idle_org/idle_{i}withcost.png")

        for i in range(1, 17):
            if i == 6:
                self.load_image(f"bullet_{i}", "resource/bullet_org/bullet_up.png")
            elif i == 7:
                self.load_image(f"bullet_{i}", "resource/bullet_org/bullet_7.png")
            else:
                self.load_image(f"bullet_{i}", f"resource/bullet_org/bullet_{i}.png")

        for i in range(1, 11):
            self.load_image(f"enemy_{i}", f"resource/enemy_org/enemy_{i}.png")

        print("--- Asset Integrity Check ---")
        suspect_red_block_files = ["resource/bullet_org/bullet_12.png"]
        for f in suspect_red_block_files:
            if os.path.exists(f):
                print(f"Note: {f} exists. If this image is red, it causes the red block issue.")
            else:
                print(f"Note: {f} is missing. Transparent placeholder used.")
        print("-----------------------------")

        self.fonts["default"] = pygame.font.SysFont("SimHei", 24)
        self.fonts["title"] = pygame.font.SysFont("Arial", 48)
        self.fonts["warning"] = pygame.font.SysFont("Arial", 120)


R = ResourceManager()
