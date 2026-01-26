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
from resources import R, resource_path
from save_manager import SaveManager
from waves import WaveManager, compute_level_difficulty, starting_money_for_level


class Game:
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
        self.levels = [
            {"id": "1-1", "theme": 1, "d": 0.0, "final": False},
            {"id": "1-2", "theme": 1, "d": 0.2, "final": False},
            {"id": "1-3", "theme": 1, "d": 0.4, "final": False},
            {"id": "1-4", "theme": 1, "d": 0.6, "final": False},
            {"id": "1-5", "theme": 1, "d": 1.0, "final": False},
            {"id": "2-1", "theme": 2, "d": 0.0, "final": False},
            {"id": "2-2", "theme": 2, "d": 0.2, "final": False},
            {"id": "2-3", "theme": 2, "d": 0.4, "final": False},
            {"id": "2-4", "theme": 2, "d": 0.6, "final": False},
            {"id": "2-5", "theme": 2, "d": 0.8, "final": True},
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

    def draw_text(self, text, x, y, font_key="default", color=BLACK, center=False):
        font = R.fonts.get(font_key, R.fonts["default"])
        surf = font.render(str(text), True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surf, rect)

    def mouse_ready(self):
        now = pygame.time.get_ticks()
        return now >= self.mouse_block_until and now >= self.mouse_cooldown_end

    def play_sfx(self, name, volume=1.0):
        snd = R.sounds.get(name)
        if not snd:
            return
        snd.set_volume(volume)
        try:
            self.sfx_channel.stop()
            self.sfx_channel.play(snd)
        except Exception:
            snd.play()

    def render_slider(self, label, value, x, y, events):
        bar_w, bar_h = 320, 12
        bar_rect = pygame.Rect(x, y + 20, bar_w, bar_h)
        pygame.draw.rect(self.screen, (210, 210, 210), bar_rect, border_radius=4)
        pygame.draw.rect(self.screen, (80, 80, 80), bar_rect, 2, border_radius=4)

        knob_x = bar_rect.x + int(bar_rect.width * max(0.0, min(1.0, value)))
        knob_rect = pygame.Rect(knob_x - 8, bar_rect.centery - 12, 16, 24)
        pygame.draw.rect(self.screen, (120, 170, 255), knob_rect, border_radius=4)
        pygame.draw.rect(self.screen, BLACK, knob_rect, 2, border_radius=4)

        self.draw_text(label, x, y - 5, "default", BLACK)
        changed = False
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if bar_rect.inflate(0, 24).collidepoint(e.pos):
                    ratio = (e.pos[0] - bar_rect.x) / bar_rect.width
                    value = max(0.0, min(1.0, ratio))
                    changed = True
        return value, changed

    def draw_guidance_overlay(self, now):
        show = now < self.guidance_show_until and not self.guidance_force_hide
        if not show:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, 200), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 205))
        self.screen.blit(overlay, (70, 120))
        pygame.draw.rect(self.screen, BLACK, (70, 120, SCREEN_WIDTH - 140, 200), 2, border_radius=12)

        lines = [
            "左键点卡牌再点格子放置 IDE，右键取消选择",
            "钱不够或卡牌冷却中会显示遮罩",
            "点右上角铲子可移除放错的位置，ESC 暂停",
            "僵尸穿过最左侧会直接失败",
        ]
        y = 160
        for line in lines:
            self.draw_text(line, 100, y, "default", BLACK)
            y += 40

    def start_story(self, key, after_state):
        self.story_active_key = key
        self.story_after_state = after_state
        self.state = "STORY"
        self.story_shown[key] = True
        self.story_start_time = pygame.time.get_ticks()
        if key == "1-1":
            snd = R.sounds.get("start")
            if snd:
                snd.set_volume(0.5)
                self.sfx_channel.play(snd)
            self.story_error_timer = self.story_start_time + 5000
            self.story_error_played = False
        else:
            self.story_error_timer = None
            self.story_error_played = False

    def update_story(self, events):
        self.screen.blit(R.get_image("bg_credits"), (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 230))
        self.screen.blit(overlay, (0, 0))

        text = self.story_texts.get(self.story_active_key, "")

        start_ts = getattr(self, "story_start_time", pygame.time.get_ticks())
        if not hasattr(self, "story_start_time"):
            self.story_start_time = start_ts
        elapsed = pygame.time.get_ticks() - start_ts
        chars_to_show = len(text)
        if text:
            chars_to_show = min(len(text), max(0, elapsed // 50))
        visible_text = text[:chars_to_show]

        lines = visible_text.split("\n") if visible_text else []
        y = 200
        for line in lines:
            self.draw_text(line, 180, y, "default", BLACK)
            y += 70

        if self.story_active_key != "final":
            self.draw_text("按任意键继续", 750, 820, "default", BLACK)

        for e in events:
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                self.story_active_key = None
                next_state = self.story_after_state or "LEVEL_SELECT"
                self.story_after_state = None
                self.story_start_time = None
                self.state = next_state
                return

            if self.story_active_key == "1-1" and self.story_error_timer:
                now = pygame.time.get_ticks()
                if not self.story_error_played and now >= self.story_error_timer:
                    self.play_sfx("error", 1.0)
                    self.story_error_played = True

    def update_main_menu(self, events):
        self.screen.blit(R.get_image("bg_main"), (0, 0))
        mx, my = pygame.mouse.get_pos()

        btn_start = pygame.Rect(90, 310, 350, 100)
        btn_load = pygame.Rect(95, 450, 425, 95)
        btn_options = pygame.Rect(1180, 760, 360, 95)
        btn_quit = pygame.Rect(95, 590, 515, 85)
        btn_credits = pygame.Rect(95, 740, 405, 85)

        if btn_start.collidepoint(mx, my):
            self.screen.blit(R.get_image("hl_start"), (0, 0))
            if self.mouse_ready() and pygame.mouse.get_pressed()[0]:
                self.state = "LEVEL_SELECT"
        elif btn_load.collidepoint(mx, my):
            self.screen.blit(R.get_image("hl_save"), (0, 0))
            if self.mouse_ready() and pygame.mouse.get_pressed()[0]:
                self.archive_mode = "main"
                self.archive_message = ""
                self.state = "ARCHIVE"
        elif btn_options.collidepoint(mx, my):
            pygame.draw.rect(self.screen, (240, 240, 240), btn_options, border_radius=8)
            pygame.draw.rect(self.screen, BLACK, btn_options, 3, border_radius=8)
            self.draw_text("OPTIONS", btn_options.centerx, btn_options.centery, "title", BLACK, center=True)
            if self.mouse_ready() and pygame.mouse.get_pressed()[0]:
                self.state = "OPTIONS"
        elif btn_quit.collidepoint(mx, my):
            self.screen.blit(R.get_image("hl_quit"), (0, 0))
            if self.mouse_ready() and pygame.mouse.get_pressed()[0]:
                self.running = False
        elif btn_credits.collidepoint(mx, my):
            self.screen.blit(R.get_image("hl_credits"), (0, 0))
            if self.mouse_ready() and pygame.mouse.get_pressed()[0]:
                self.credits_page = 0
                self.state = "CREDITS"

        # Render options button when not hovered to keep it visible.
        if not btn_options.collidepoint(mx, my):
            pygame.draw.rect(self.screen, (220, 220, 220), btn_options, border_radius=8)
            pygame.draw.rect(self.screen, (60, 60, 60), btn_options, 2, border_radius=8)
            self.draw_text("OPTIONS", btn_options.centerx, btn_options.centery, "title", BLACK, center=True)

    def update_options(self, events):
        self.screen.blit(R.get_image("bg_credits"), (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 230))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(380, 180, 840, 500)
        pygame.draw.rect(self.screen, (245, 245, 245), panel, border_radius=12)
        pygame.draw.rect(self.screen, (70, 70, 70), panel, 3, border_radius=12)

        self.draw_text("OPTIONS", panel.centerx - 70, panel.top + 30, "title", BLACK)
        self.draw_text("Click the bar to set volume", panel.centerx - 170, panel.top + 90, "default", BLACK)

        music_val = self.settings.get("music_volume", 0.1)
        new_music, music_changed = self.render_slider("Music Volume", music_val, panel.left + 120, panel.top + 140, events)
        if music_changed:
            self.settings["music_volume"] = new_music
            try:
                pygame.mixer.music.set_volume(new_music)
            except Exception:
                pass
            self.options_dirty = True

        sfx_val = self.settings.get("sfx_volume", 1.0)
        new_sfx, sfx_changed = self.render_slider("SFX Volume", sfx_val, panel.left + 120, panel.top + 230, events)
        if sfx_changed:
            self.settings["sfx_volume"] = new_sfx
            self.sfx_channel.set_volume(new_sfx)
            self.lose_sound_channel.set_volume(new_sfx)
            self.options_dirty = True

        back_rect = pygame.Rect(panel.centerx - 120, panel.bottom - 120, 240, 70)
        pygame.draw.rect(self.screen, (220, 220, 220), back_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, back_rect, 2, border_radius=10)
        self.draw_text("BACK", back_rect.centerx, back_rect.centery, "title", BLACK, center=True)

        mx, my = pygame.mouse.get_pos()
        if back_rect.collidepoint(mx, my):
            pygame.draw.rect(self.screen, HOVER_COLOR, back_rect, 3, border_radius=10)
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.leave_options()

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.leave_options()

    def leave_options(self):
        if self.options_dirty:
            self.save_data["settings"] = self.settings
            SaveManager.save(self.save_data)
            self.options_dirty = False
        self.state = "MAIN_MENU"

    def update_level_select(self, events):
        self.screen.blit(R.get_image("bg_credits"), (0, 0))
        mx, my = pygame.mouse.get_pos()

        processed_click = False
        for e in events:
            if e.type == pygame.MOUSEBUTTONUP:
                processed_click = True

        for lvl in self.levels:
            lid = lvl["id"]
            rect = self.level_buttons.get(lid)
            if not rect:
                continue

            theme = str(lvl["theme"])
            idx = int(lid.split("-")[1])
            unlocked_upto = self.save_data["unlocked"].get(theme, 1)
            is_unlocked = self.debug_mode or idx <= unlocked_upto

            pygame.draw.rect(self.screen, (30, 30, 30), rect, 2)
            self.draw_text(lid, rect.x + 20, rect.y + 30, "default", BLACK)

            if is_unlocked:
                if rect.collidepoint(mx, my):
                    hover = pygame.transform.smoothscale(R.get_image("level_hover"), (200, 90))
                    self.screen.blit(hover, rect)
                    if processed_click and rect.collidepoint(mx, my):
                        self.selected_level = lvl
                        self.selected_plants_indices = []
                        if lid == "1-1" and not self.story_shown["1-1"]:
                            self.start_story("1-1", "PLANT_SELECT")
                        elif lid == "2-1" and not self.story_shown["2-1"]:
                            self.start_story("2-1", "PLANT_SELECT")
                        else:
                            self.state = "PLANT_SELECT"
            else:
                shade = pygame.Surface((200, 90))
                shade.fill(BLACK)
                shade.set_alpha(150)
                self.screen.blit(shade, rect)

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = "MAIN_MENU"

    def update_plant_select(self, events):
        self.screen.blit(R.get_image("bg_credits"), (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 220))
        self.screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(
            SELECT_START_X - 30,
            SELECT_START_Y - 30,
            SELECT_GAP_X * 3 + SELECT_SLOT_SIZE + 60,
            SELECT_GAP_Y * 3 + SELECT_SLOT_SIZE + 100,
        )
        pygame.draw.rect(self.screen, (50, 50, 50), panel_rect, 5, border_radius=15)
        self.draw_text("CHOOSE YOUR IDES", panel_rect.centerx - 230, panel_rect.top - 45, "title", BLACK)

        mx, my = pygame.mouse.get_pos()
        hovered_plant_idx = -1
        available = [i for i in range(16) if i not in self.selected_plants_indices]

        for idx in range(16):
            if idx in self.selected_plants_indices:
                continue

            slot_rect = self.plant_select_rects[idx]
            pygame.draw.rect(self.screen, (200, 200, 200), slot_rect, border_radius=5)
            pygame.draw.rect(self.screen, (80, 80, 80), slot_rect, 2, border_radius=5)

            img = R.get_image(f"idle_{idx+1}withcost")
            img_rect = img.get_rect(center=slot_rect.center)
            self.screen.blit(img, img_rect)

            if slot_rect.collidepoint(mx, my):
                pygame.draw.rect(self.screen, HOVER_COLOR, slot_rect, 3, border_radius=5)
                hovered_plant_idx = idx
                for e in events:
                    if e.type == pygame.MOUSEBUTTONUP:
                        if len(self.selected_plants_indices) < 10:
                            self.selected_plants_indices.append(idx)

        for i, p_idx in enumerate(self.selected_plants_indices):
            x, y = 100 + i * 110, 75
            sel_rect = pygame.Rect(x, y, 90, 90)

            pygame.draw.rect(self.screen, (230, 230, 255), sel_rect, border_radius=5)
            pygame.draw.rect(self.screen, BLACK, sel_rect, 2, border_radius=5)

            img = R.get_image(f"idle_{p_idx+1}withcost")
            ir = img.get_rect(center=sel_rect.center)
            self.screen.blit(img, ir)

            if sel_rect.collidepoint(mx, my):
                pygame.draw.rect(self.screen, RED, sel_rect, 3, border_radius=5)
                for e in events:
                    if e.type == pygame.MOUSEBUTTONUP:
                        self.selected_plants_indices.pop(i)
                        break

        pygame.draw.rect(self.screen, BLACK, self.ok_button, 3)
        self.draw_text("OK!!", self.ok_button.x + 30, self.ok_button.y + 20, "default", BLACK)

        if self.ok_button.collidepoint(mx, my):
            pygame.draw.rect(self.screen, HOVER_COLOR, self.ok_button, 3)
            for e in events:
                if e.type == pygame.MOUSEBUTTONUP and len(self.selected_plants_indices) > 0:
                    self.start_game()

        if hovered_plant_idx != -1:
            stats = PLANT_STATS[hovered_plant_idx]
            tip_w, tip_h = 300, 120
            tip_x = mx + 15
            tip_y = my + 15
            if tip_x + tip_w > SCREEN_WIDTH:
                tip_x = mx - tip_w - 15
            if tip_y + tip_h > SCREEN_HEIGHT:
                tip_y = my - tip_h - 15

            pygame.draw.rect(self.screen, (240, 240, 240), (tip_x, tip_y, tip_w, tip_h))
            pygame.draw.rect(self.screen, BLACK, (tip_x, tip_y, tip_w, tip_h), 2)

            self.draw_text(stats["name"], tip_x + 10, tip_y + 10, "default", BLACK)
            self.draw_text(f"Cost: {stats['cost']}", tip_x + 10, tip_y + 40, "default", BLACK)
            self.draw_text(f"HP: {stats['hp']} Dmg: {stats['damage']}", tip_x + 10, tip_y + 65, "default", BLACK)
            self.draw_text(stats["desc"], tip_x + 10, tip_y + 90, "default", (50, 50, 50))

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = "LEVEL_SELECT"

    def start_game(self):
        self.state = "GAMING"
        difficulty = compute_level_difficulty(self.selected_level)
        self.money = starting_money_for_level(self.selected_level)
        self.plants.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.wave_manager = WaveManager(self.selected_level, difficulty)
        now = pygame.time.get_ticks()
        self.game_start_tick = now
        self.guidance_show_until = now + 20000
        self.guidance_force_hide = False
        self.enemies_killed = 0
        self.win_sound_played = False

        self.plant_cd_status = {}
        for idx in self.selected_plants_indices:
            self.plant_cd_status[idx] = -99999

    def update_gaming(self, events):
        now = pygame.time.get_ticks()
        elapsed = now - self.game_start_tick

        self.screen.fill(BLACK)

        bg = R.get_image("bg_game2") if self.selected_level["theme"] == 2 else R.get_image("bg_game1")
        self.screen.blit(bg, (0, 0))

        if elapsed > self.spawn_delay:
            spawns = self.wave_manager.update(now)
            for (e_id, row) in spawns:
                self.enemies.add(Enemy(e_id, row))

        if now % 1000 < 20:
            pass

        self.plants.update(now, self.enemies, self.bullets, game_ref=self)
        self.bullets.update()
        self.enemies.update(self.plants)

        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, False)
        for enemy, hit_bullets in hits.items():
            if not enemy.alive():
                continue

            total_damage = 0
            for b in hit_bullets:
                total_damage += b.damage
                b.kill()

            enemy.hp -= total_damage

            if enemy.hp <= 0 and enemy.alive():
                enemy.kill()
                self.money += enemy.reward
                self.enemies_killed += 1

        for enemy in list(self.enemies):
            if enemy.hp <= 0 and enemy.alive():
                enemy.kill()
                self.money += enemy.reward
                self.enemies_killed += 1

        if self.wave_manager:
            spawning_done = self.wave_manager.finished_spawning

            if spawning_done:
                for e in list(self.enemies):
                    if e.rect.x >= SCREEN_WIDTH:
                        e.kill()

            alive = len(self.enemies)

            if self.debug_mode:
                if now - self.last_debug_log > 1000:
                    self.last_debug_log = now
                    print(f"DEBUG WIN CHECK -> alive: {alive}, spawning_done: {spawning_done}")
                    for e in self.enemies:
                        print(f"  Enemy id={e.id} row={e.row} x={e.rect.x} hp={e.hp} frozen={e.frozen}")
                self.draw_text(f"Alive: {alive} | Spawning Done: {spawning_done}", 20, 210, "default", BLACK)

            if spawning_done and alive == 0:
                if self.selected_level and self.selected_level.get("final") and not self.story_shown["final"]:
                    self.start_story("final", "WIN")
                else:
                    self.play_sfx("win", 1.0)
                    self.state = "WIN"
                return

        for e in list(self.enemies):
            if e.rect.x > SCREEN_WIDTH + 200 or e.rect.x < -200:
                e.kill()
            elif e.hp <= 0:
                e.kill()

        for e in self.enemies:
            if e.rect.x < 200:
                self.state = "LOSE"
                self.lose_sound_sequence = ["error1"] * 5 + ["error"]
                self.lose_sound_index = 0
                self.lose_sound_active = True
                if self.lose_sound_channel:
                    self.lose_sound_channel.stop()
                return

        self.draw_text(str(self.money), 90, 100, "default", BLACK)

        mx, my = pygame.mouse.get_pos()

        for i, slot_rect in enumerate(self.slot_rects):
            if i >= len(self.selected_plants_indices):
                break
            p_idx = self.selected_plants_indices[i]
            img = R.get_image(f"idle_{p_idx+1}withcost")
            self.screen.blit(img, slot_rect.topleft)

            stats = PLANT_STATS[p_idx]
            last_p = self.plant_cd_status.get(p_idx, 0)
            cd_remain = stats["cooldown"] - (now - last_p)
            if cd_remain > 0:
                ratio = cd_remain / stats["cooldown"]
                h = int(100 * ratio)
                mask = pygame.Surface((100, h))
                mask.fill(BLACK)
                mask.set_alpha(150)
                self.screen.blit(mask, (slot_rect.x, slot_rect.y + (100 - h)))

            if self.money < stats["cost"]:
                self.screen.blit(R.get_image("no_money"), (slot_rect.x, slot_rect.y - 10))

            if slot_rect.collidepoint(mx, my):
                if self.mouse_ready() and pygame.mouse.get_pressed()[0] and not self.holding_shovel:
                    if cd_remain <= 0 and self.money >= stats["cost"]:
                        self.holding_plant_idx = i

        self.screen.blit(R.get_image("cleaner"), self.shovel_rect)
        if self.shovel_rect.collidepoint(mx, my):
            if self.mouse_ready() and pygame.mouse.get_pressed()[0]:
                self.holding_shovel = True
                self.holding_plant_idx = -1

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                self.holding_plant_idx = -1
                self.holding_shovel = False

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                c = (mx - GRID_START_X) // CELL_WIDTH
                r = (my - GRID_START_Y) // CELL_HEIGHT

                if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                    if self.holding_shovel:
                        for p in self.plants:
                            if p.row == r and p.col == c:
                                p.kill()
                                self.holding_shovel = False
                                rm = R.sounds.get("remove")
                                if rm:
                                    try:
                                        self.sfx_channel.play(rm)
                                    except Exception:
                                        rm.play()
                                break
                    elif self.holding_plant_idx != -1:
                        occupied = any(p.row == r and p.col == c for p in self.plants)
                        if not occupied:
                            p_idx = self.selected_plants_indices[self.holding_plant_idx]
                            stats = PLANT_STATS[p_idx]
                            self.money -= stats["cost"]
                            self.plants.add(Plant(p_idx, (r, c)))
                            self.plant_cd_status[p_idx] = now
                            self.holding_plant_idx = -1
                            st = R.sounds.get("set")
                            if st:
                                try:
                                    self.sfx_channel.play(st)
                                except Exception:
                                    st.play()

            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = "PAUSE"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_h:
                self.guidance_force_hide = not self.guidance_force_hide
                if not self.guidance_force_hide:
                    self.guidance_show_until = max(self.guidance_show_until, now + 12000)

        self.plants.draw(self.screen)
        self.enemies.draw(self.screen)
        self.bullets.draw(self.screen)

        self.draw_guidance_overlay(now)

        if self.warning_time < elapsed < self.spawn_delay:
            if (elapsed // 200) % 2 == 0:
                txt = "YOUR BUGS ARE COMING!!!"
                font = R.fonts.get("warning", pygame.font.SysFont(None, 120))
                surf = font.render(txt, True, RED)
                rect = surf.get_rect(center=(800, 280))
                self.screen.blit(surf, rect)

        if self.holding_plant_idx != -1:
            p_idx = self.selected_plants_indices[self.holding_plant_idx]
            img = R.get_image(f"idle_{p_idx+1}withcost")
            self.screen.blit(img, (mx - 50, my - 50))
        elif self.holding_shovel:
            self.screen.blit(R.get_image("cleaner"), (mx - 50, my - 50))

    def update_pause(self, events):
        darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        darkness.fill(BLACK)
        darkness.set_alpha(150)
        self.screen.blit(darkness, (0, 0))

        p_img = R.get_image("bg_pause")
        p_rect = p_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(p_img, p_rect)

        if not hasattr(self, "pause_start_ts"):
            self.pause_start_ts = pygame.time.get_ticks()

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    self.state = "GAMING"
                    pause_duration = pygame.time.get_ticks() - self.pause_start_ts
                    self.game_start_tick += pause_duration
                    for idx in self.plant_cd_status:
                        self.plant_cd_status[idx] += pause_duration
                    delattr(self, "pause_start_ts")
                elif e.key == pygame.K_ESCAPE:
                    self.state = "MAIN_MENU"
                    if hasattr(self, "pause_start_ts"):
                        delattr(self, "pause_start_ts")

    def update_win(self, events):
        if self.selected_level.get("final") and not getattr(self, "win_sound_played", False):
            self.play_sfx("win", 1.0)
            self.win_sound_played = True
        if self.selected_level["final"]:
            if self.win_anim_start is None:
                self.win_anim_start = pygame.time.get_ticks()
            img = R.get_image("img_win_final")
            elapsed = pygame.time.get_ticks() - self.win_anim_start
            duration = 800
            t = min(1.0, elapsed / duration)
            start_scale = 0.25
            end_scale = 1.05
            scale = start_scale + (end_scale - start_scale) * t
            target_w = int(SCREEN_WIDTH * scale)
            target_h = int(SCREEN_HEIGHT * scale)
            scaled = pygame.transform.smoothscale(img, (target_w, target_h))
            rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(scaled, rect)
            self.draw_text("按任意键返回选关", 650, 820, "default", BLACK)
        else:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(WHITE)
            overlay.set_alpha(100)
            self.screen.blit(overlay, (0, 0))

            self.draw_text("YOU WIN!", 800, 450, "warning", BLACK, True)

        if self.selected_level:
            theme = str(self.selected_level["theme"])
            lid = int(self.selected_level["id"].split("-")[1])
            if lid < 5:
                curr = self.save_data["unlocked"].get(theme, 1)
                if lid >= curr:
                    self.save_data["unlocked"][theme] = lid + 1
                    SaveManager.save(self.save_data)
            elif lid == 5 and theme == "1":
                if self.save_data["unlocked"].get("2", 0) == 0:
                    self.save_data["unlocked"]["2"] = 1
                    SaveManager.save(self.save_data)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN or e.type == pygame.KEYDOWN:
                self.win_anim_start = None
                self.state = "LEVEL_SELECT"

    def update_lose(self, events):
        darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        darkness.fill(BLACK)
        darkness.set_alpha(150)
        self.screen.blit(darkness, (0, 0))

        l_img = R.get_image("img_lose")
        l_rect = l_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(l_img, l_rect)

        r_img = R.get_image("img_return")
        r_rect = r_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        self.screen.blit(r_img, r_rect)

        if self.lose_sound_active and self.lose_sound_index < len(self.lose_sound_sequence):
            if not self.lose_sound_channel.get_busy():
                key = self.lose_sound_sequence[self.lose_sound_index]
                self.sfx_channel.stop()
                self.play_sfx(key, 1.0)
                self.lose_sound_index += 1
            if self.lose_sound_index >= len(self.lose_sound_sequence) and not self.lose_sound_channel.get_busy():
                self.lose_sound_active = False

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = "LEVEL_SELECT"

    def update_credits(self, events):
        self.screen.fill(WHITE)

        key = f"credits{2 + (self.credits_page % 4)}"
        img = R.get_image(key)
        if img:
            self.screen.blit(img, (0, 0))

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.state = "MAIN_MENU"
                    return
                if e.key == pygame.K_LEFT:
                    self.credits_page = (self.credits_page - 1) % 4
                if e.key == pygame.K_RIGHT:
                    self.credits_page = (self.credits_page + 1) % 4

        self.draw_text(f"{(self.credits_page % 4) + 1}/4", SCREEN_WIDTH - 80, 20, "default", BLACK)

    def update_archive(self, events):
        if self.archive_mode in ("tips", "ide", "bug"):
            if self.archive_mode == "tips":
                keys = ARCHIVE_HELP_KEYS
            elif self.archive_mode == "ide":
                keys = ARCHIVE_IDE_KEYS
            else:
                keys = ARCHIVE_BUG_KEYS

            key = keys[self.archive_page % len(keys)]
            img = R.get_image(key)
            self.screen.blit(img, (0, 0))

            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.archive_mode = "main"
                        return
                    if e.key == pygame.K_LEFT:
                        self.archive_page = (self.archive_page - 1) % len(keys)
                    if e.key == pygame.K_RIGHT:
                        self.archive_page = (self.archive_page + 1) % len(keys)

            self.draw_text(f"{self.archive_page + 1}/{len(keys)}", 1550, 20, "default", BLACK)
            return

        self.screen.blit(R.get_image("bg_archive"), (0, 0))

        mx, my = pygame.mouse.get_pos()
        for btn in ARCHIVE_BUTTONS:
            area_rect = pygame.Rect(btn["pos"][0], btn["pos"][1], btn["area_size"][0], btn["area_size"][1])

            for e in events:
                if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    if area_rect.collidepoint(e.pos):
                        if btn["name"] == "游玩提示":
                            self.archive_mode = "tips"
                            self.archive_page = 0
                        elif btn["name"] == "植物IDE图鉴":
                            self.archive_mode = "ide"
                            self.archive_page = 0
                        elif btn["name"] == "僵尸BUG图鉴":
                            self.archive_mode = "bug"
                            self.archive_page = 0

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = "MAIN_MENU"


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
