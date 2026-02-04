import pygame
from constants import BLACK, SCREEN_HEIGHT, SCREEN_WIDTH
from resources import R


class GameCommonMixin:
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
        self.screen.blit(overlay, (70, 140))
        pygame.draw.rect(self.screen, BLACK, (70, 140, SCREEN_WIDTH - 140, 200), 2, border_radius=12)

        lines = [
            "左键点卡牌再点格子放置 IDE，右键取消选择",
            "钱不够或卡牌冷却中会显示遮罩",
            "点右上角垃圾桶可移除放错的位置，ESC 暂停",
            "僵尸穿过最左侧会直接失败",
        ]
        y = 180
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
