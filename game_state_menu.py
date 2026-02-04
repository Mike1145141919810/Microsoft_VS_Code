import pygame
from constants import (
    ARCHIVE_BUG_KEYS,
    ARCHIVE_BUTTONS,
    ARCHIVE_HELP_KEYS,
    ARCHIVE_IDE_KEYS,
    BLACK,
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
)
from resources import R
from save_manager import SaveManager


class GameMenuMixin:
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
        _ = available

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
        _ = (mx, my)
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
