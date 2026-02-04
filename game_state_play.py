import pygame
from constants import (
    BLACK,
    CELL_HEIGHT,
    CELL_WIDTH,
    GRID_COLS,
    GRID_ROWS,
    GRID_START_X,
    GRID_START_Y,
    PLANT_STATS,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)
from entities import Enemy, Plant
from resources import R
from save_manager import SaveManager
from waves import EndlessWaveManager, WaveManager, compute_level_difficulty, starting_money_for_level


class GamePlayMixin:
    def start_game(self):
        self.state = "GAMING"
        if self.game_mode == "ENDLESS":
            if not self.selected_level:
                self.selected_level = {"id": "ENDLESS", "theme": 1, "d": 0.4, "final": False}
            difficulty = 1.0
            self.money = starting_money_for_level(self.selected_level)
        else:
            difficulty = compute_level_difficulty(self.selected_level)
            self.money = starting_money_for_level(self.selected_level)
        self.plants.empty()
        self.enemies.empty()
        self.bullets.empty()
        if self.game_mode == "ENDLESS":
            self.wave_manager = EndlessWaveManager(difficulty=difficulty)
        else:
            self.wave_manager = WaveManager(self.selected_level, difficulty)
        now = pygame.time.get_ticks()
        self.game_start_tick = now
        self.guidance_show_until = now + 20000
        self.guidance_force_hide = False
        self.lose_transition_start = None
        self.lose_enemy_pos = None
        self.lose_enemy_start = None
        self.lose_enemy_img_key = None
        self.lose_cam_offset = 0
        self.lose_enemy_id = None
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

        if self.wave_manager and self.game_mode != "ENDLESS":
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
                self.lose_transition_start = pygame.time.get_ticks()
                self.lose_cam_offset = 0
                self.lose_enemy_start = (e.rect.centerx, e.rect.centery)
                self.lose_enemy_pos = list(self.lose_enemy_start)
                self.lose_enemy_img_key = f"enemy_{e.id+1}"
                self.lose_enemy_id = e.id
                if self.lose_sound_channel:
                    self.lose_sound_channel.stop()
                return

        self.draw_text(str(self.money), 90, 100, "default", BLACK)

        if self.game_mode == "ENDLESS" and self.wave_manager and getattr(self.wave_manager, "wave_started_ts", 0):
            wave_ts = self.wave_manager.wave_started_ts
            if now - wave_ts < 2500:
                wave_num = getattr(self.wave_manager, "wave_index", 1)
                self.draw_text(f"第{wave_num}波", SCREEN_WIDTH // 2 - 60, 140, "title", RED)

        mx, my = pygame.mouse.get_pos()

        hovered_slot_idx = None

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
                hovered_slot_idx = p_idx

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

        if hovered_slot_idx is not None:
            stats = PLANT_STATS[hovered_slot_idx]
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
        now = pygame.time.get_ticks()
        elapsed = 0
        if self.lose_transition_start:
            elapsed = now - self.lose_transition_start

        bg_lose = R.get_image("img_lose_bg") or R.get_image("bg_game1")
        bg_map = R.get_image("bg_game2") if self.selected_level and self.selected_level.get("theme") == 2 else R.get_image("bg_game1")
        cam_range = SCREEN_WIDTH  # push everything fully off-screen to the right
        cam_dur = 1500
        self.lose_cam_offset = min(cam_range, int(cam_range * (elapsed / cam_dur))) if cam_dur > 0 else cam_range

        # Clear then draw lose background sliding in from left while map/objects slide right.
        self.screen.fill(BLACK)

        progress = 0 if cam_dur <= 0 else min(1.0, elapsed / cam_dur)
        map_offset = int(cam_range * progress)  # map and objects move right
        lose_offset = -SCREEN_WIDTH + map_offset  # lose bg enters from left to 0

        if bg_lose:
            x1 = lose_offset
            x2 = x1 + SCREEN_WIDTH
            self.screen.blit(bg_lose, (x1, 0))
            self.screen.blit(bg_lose, (x2, 0))

        if bg_map:
            self.screen.blit(bg_map, (map_offset, 0))

        draw_offset = map_offset

        # Draw world objects frozen in place, shifted with the camera pan.
        for p in self.plants:
            if not hasattr(p, "image"):
                continue
            rect = p.rect.copy()
            rect.x += draw_offset
            self.screen.blit(p.image, rect)

        for b in self.bullets:
            if not hasattr(b, "image"):
                continue
            rect = b.rect.copy()
            rect.x += draw_offset
            self.screen.blit(b.image, rect)

        for en in self.enemies:
            if not hasattr(en, "image"):
                continue
            is_target = self.lose_enemy_id is not None and en.id == self.lose_enemy_id
            if is_target:
                # Target enemy drawn separately after camera move.
                continue
            rect = en.rect.copy()
            rect.x += draw_offset
            self.screen.blit(en.image, rect)

        target_move_done = False
        if self.lose_enemy_pos and self.lose_enemy_img_key and self.lose_enemy_start:
            move_dur = 1400
            move_delay = cam_dur
            move_elapsed = max(0, elapsed - move_delay)
            t = min(1.0, move_elapsed / move_dur) if move_dur > 0 else 1.0
            sx = self.lose_enemy_start[0] + cam_range
            sy = self.lose_enemy_start[1]
            tx, ty = self.lose_enemy_target
            cx = sx + (tx - sx) * t
            cy = sy + (ty - sy) * t
            self.lose_enemy_pos = [cx, cy]
            e_img = R.get_image(self.lose_enemy_img_key)
            if e_img:
                e_rect = e_img.get_rect(center=(int(cx), int(cy)))
                self.screen.blit(e_img, e_rect)
            if t >= 1.0:
                target_move_done = True

        if target_move_done:
            if self.lose_sound_active and self.lose_sound_index < len(self.lose_sound_sequence):
                if not self.sfx_channel.get_busy():
                    key = self.lose_sound_sequence[self.lose_sound_index]
                    self.sfx_channel.stop()
                    self.play_sfx(key, 1.0)
                    self.lose_sound_index += 1
                if self.lose_sound_index >= len(self.lose_sound_sequence) and not self.sfx_channel.get_busy():
                    self.lose_sound_active = False

        show_ui = target_move_done and (
            not self.lose_sound_active
            or (self.lose_sound_index >= len(self.lose_sound_sequence) and not self.sfx_channel.get_busy())
        )
        if show_ui:
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

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = "LEVEL_SELECT"
