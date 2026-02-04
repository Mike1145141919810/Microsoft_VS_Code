import sys
import pygame
from constants import (
    ARCHIVE_BUG_KEYS,
    ARCHIVE_BUTTONS,
    ARCHIVE_HELP_KEYS,
    ARCHIVE_IDE_KEYS,
    BLACK,
    CELL_HEIGHT,
    CELL_WIDTH,
    GRID_COLS,
    GRID_ROWS,
    GRID_START_X,
    GRID_START_Y,
    HOVER_COLOR,
    PLANT_STATS,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SELECT_GAP_X,
    SELECT_GAP_Y,
    SELECT_SLOT_SIZE,
    SELECT_START_X,
    SELECT_START_Y,
    WHITE,
    FPS,
)
from entities import Plant, Enemy
from game_common import GameCommonMixin
from game_state_menu import GameMenuMixin
from game_state_play import GamePlayMixin
from resources import R, resource_path
from save_manager import SaveManager
from waves import WaveManager, compute_level_difficulty, starting_money_for_level


class Game(GameCommonMixin, GameMenuMixin, GamePlayMixin):
    def __init__(self):
        pg = pygame
        pg.init()
        pygame.mixer.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Microsoft VS Code - Rewritten")
        self.clock = pg.time.Clock()
        self.running = True

        R.load_assets()
        self.sfx_channel = pygame.mixer.Channel(6)
        self.lose_sound_channel = pygame.mixer.Channel(7)
        try:
            pygame.mixer.music.load(resource_path("resource/sounds/bgm.wav"))
        except Exception as e:
            print(f"BGM load/play failed: {e}")
        self.save_data = SaveManager.load()
        self.settings = self.save_data.setdefault("settings", {})
        self.settings.setdefault("music_volume", 0.1)
        self.settings.setdefault("sfx_volume", 1.0)
        self.options_dirty = False

        sfx_vol = self.settings.get("sfx_volume", 1.0)
        music_vol = self.settings.get("music_volume", 0.1)
        self.sfx_channel.set_volume(sfx_vol)
        self.lose_sound_channel.set_volume(sfx_vol)
        try:
            pygame.mixer.music.set_volume(music_vol)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

        self.state = "MAIN_MENU"
        self.game_mode = "STORY"
        self.levels = [
            {"id": "1-1", "theme": 1, "d": 0.0, "final": False},
            {"id": "1-2", "theme": 1, "d": 0.2, "final": False},
            {"id": "1-3", "theme": 1, "d": 0.4, "final": False},
            {"id": "1-4", "theme": 1, "d": 0.6, "final": False},
            {"id": "1-5", "theme": 1, "d": 0.8, "final": False},
            {"id": "2-1", "theme": 2, "d": 0.0, "final": False},
            {"id": "2-2", "theme": 2, "d": 0.2, "final": False},
            {"id": "2-3", "theme": 2, "d": 0.4, "final": False},
            {"id": "2-4", "theme": 2, "d": 0.6, "final": False},
            {"id": "2-5", "theme": 2, "d": 1.0, "final": True},
        ]

        self.level_buttons = {}
        y_base_1 = 260
        y_base_2 = 520
        x_start = 180
        box_w, box_h = 200, 90
        gap = 240
        for i in range(5):
            self.level_buttons[f"1-{i+1}"] = pygame.Rect(x_start + i * gap, y_base_1, box_w, box_h)
            self.level_buttons[f"2-{i+1}"] = pygame.Rect(x_start + i * gap, y_base_2, box_w, box_h)

        self.selected_level = None
        self.selected_plants_indices = []

        self.plants = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.money = 3000
        self.wave_manager = None
        self.game_start_tick = 0
        self.spawn_delay = 30000
        self.warning_time = 25000
        self.win_sound_played = False

        self.mouse_cooldown_end = 0
        self.mouse_block_until = 0

        self.plant_select_rects = []
        for r in range(4):
            for c in range(4):
                x = SELECT_START_X + c * SELECT_GAP_X
                y = SELECT_START_Y + r * SELECT_GAP_Y
                self.plant_select_rects.append(pygame.Rect(x, y, SELECT_SLOT_SIZE, SELECT_SLOT_SIZE))
        self.ok_button = pygame.Rect(1350, 780, 150, 80)
        self.mode_story_rect = pygame.Rect(80, 360, 600, 220)
        self.mode_endless_rect = pygame.Rect(920, 360, 600, 220)

        self.slot_rects = []
        for i in range(10):
            self.slot_rects.append(pygame.Rect(220 + i * 120, 10, 100, 100))
        self.shovel_rect = pygame.Rect(1455, 5, 100, 100)
        self.holding_plant_idx = -1
        self.holding_shovel = False

        self.debug_ups = 0
        self.debug_last = 0
        self.debug_mode = False
        self.last_debug_log = 0
        self.archive_message = ""
        self.archive_mode = "main"
        self.archive_page = 0
        self.credits_page = 0

        self.story_shown = {"1-1": False, "2-1": False, "final": False}
        self.story_texts = {
            "1-1": "第一章\n你是计算机专业的大学生，正趴在宿舍桌前用VS Code写代码。\n赶ddl的压力让你手忙脚乱，屏幕上堆了一堆没调试完的代码，桌面也乱得全是文件图标。\n突然，屏幕一闪，那些没修好的BUG竟然活了过来，变成一个个黑糊糊的小僵尸，顺着屏幕边缘爬出来，\n开始啃咬你桌面上的文件——再不管，你的作业就要被它们毁完了！",
            "2-1": "第二章\n他们爬进了你的编辑器！！这里藏着你所有的项目代码和作业草稿，要是被它们毁了，整个学期的努力都白费。\n更麻烦的是，编辑器里的BUG僵尸变得更强了...",
            "final": "最终结算\n恭喜你de完了所有bug!你完成了作业沉沉睡去...",
        }
        self.story_after_state = None
        self.story_active_key = None
        self.story_error_timer = None
        self.story_error_played = False

        self.win_anim_start = None
        self.lose_sound_sequence = []
        self.lose_sound_index = 0
        self.lose_sound_channel = pygame.mixer.Channel(7)
        self.lose_sound_active = False
        self.lose_transition_start = None
        self.lose_cam_offset = 0
        self.lose_enemy_pos = None
        self.lose_enemy_start = None
        self.lose_enemy_target = (978, 460)
        self.lose_enemy_img_key = None
        self.lose_enemy_id = None

        self.guidance_force_hide = False
        self.guidance_show_until = 0

    def run(self):
        while self.running:
            raw_events = pygame.event.get()
            now = pygame.time.get_ticks()

            events = []
            for e in raw_events:
                if e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    if now < self.mouse_block_until or now < self.mouse_cooldown_end:
                        continue
                    if e.type == pygame.MOUSEBUTTONUP:
                        self.mouse_cooldown_end = now + 100
                events.append(e)

            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_UP:
                    self.debug_mode = not self.debug_mode
                    self.save_data["unlocked"]["1"] = 5
                    self.save_data["unlocked"]["2"] = 5
                    SaveManager.save(self.save_data)

            state_before = self.state
            if self.state == "MAIN_MENU":
                self.update_main_menu(events)
            elif self.state == "LEVEL_SELECT":
                self.update_level_select(events)
            elif self.state == "MODE_SELECT":
                self.update_mode_select(events)
            elif self.state == "PLANT_SELECT":
                self.update_plant_select(events)
            elif self.state == "GAMING":
                self.update_gaming(events)
            elif self.state == "PAUSE":
                self.update_pause(events)
            elif self.state == "WIN":
                self.update_win(events)
            elif self.state == "LOSE":
                self.update_lose(events)
            elif self.state == "ARCHIVE":
                self.update_archive(events)
            elif self.state == "CREDITS":
                self.update_credits(events)
            elif self.state == "OPTIONS":
                self.update_options(events)
            elif self.state == "STORY":
                self.update_story(events)

            if self.state != state_before:
                self.mouse_block_until = pygame.time.get_ticks() + 200

            self.clock.tick(FPS)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
