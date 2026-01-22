import pygame
import sys
import json
import random
import os

# Helper to resolve data files when bundled (PyInstaller) or running from source
def resource_path(rel_path):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)

# --- Configuration & Constants ---
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60
SAVE_PATH = "save.json"

# Archive buttons layout
ARCHIVE_BUTTONS = [
    {
        "name": "植物IDE图鉴",
        "text": "植物IDE图鉴",
        "pos": (110, 250),
        "area_size": (360, 538),
        "text_pos": (128, 750),
        "text_size": (327, 63)
    },
    {
        "name": "僵尸BUG图鉴",
        "text": "僵尸BUG图鉴",
        "pos": (620, 250),
        "area_size": (360, 538),
        "text_pos": (620, 750),
        "text_size": (355, 63)
    },
    {
        "name": "游玩提示",
        "text": "游玩提示！",
        "pos": (1130, 250),
        "area_size": (360, 538),
        "text_pos": (1165, 750),
        "text_size": (291, 63)
    }
]

ARCHIVE_HELP_KEYS = ["archive_help_1", "archive_help_2"]
ARCHIVE_IDE_KEYS = [
    "植物page1", "植物page2", "植物page3",
    "植物page4", "植物page5", "植物page6"
]
ARCHIVE_BUG_KEYS = [
    "BUGspage1", "BUGspage2", "BUGspage3", "BUGspage4"
]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
HOVER_COLOR = (255, 255, 0)

# Grid Configuration
GRID_ROWS = 5
GRID_COLS = 10
GRID_START_X = 275
GRID_START_Y = 265
CELL_WIDTH = 135
CELL_HEIGHT = 130

# Plant Select Grid
SELECT_SLOT_SIZE = 100
SELECT_START_X = 210
SELECT_START_Y = 240  # shifted down 15px per request
SELECT_GAP_X = 170
SELECT_GAP_Y = 125

# Stats (Halved Speed applied here directly)
# Format: [HP, AttackSpeed(unused/handled by logic), MoveSpeed, DropMoney]
# Original speeds were [3, 5, 2, 2, 2.5, 1.5, 0.75, 0.5, 2, 2]
# Applied 0.5 multiplier
ENEMY_STATS = {
    0: {"hp": 80,  "speed": 1.5,  "reward": 15}, # Syntax/Compile Error
    1: {"hp": 80,  "speed": 2.5,  "reward": 20}, # Null Pointer
    2: {"hp": 200, "speed": 1.0,  "reward": 25}, # Infinite Loop
    3: {"hp": 300, "speed": 1.0,  "reward": 40}, # Memory Overflow
    4: {"hp": 200, "speed": 1.25, "reward": 20}, # Array Index Out
    5: {"hp": 450, "speed": 0.75, "reward": 50}, # Stack Overflow
    6: {"hp": 500, "speed": 0.375,"reward": 10}, # Memory Leak
    7: {"hp": 600, "speed": 0.25, "reward": 80}, # No Idea
    8: {"hp": 300, "speed": 1.0,  "reward": 40}, # Missing Runtime
    9: {"hp": 250, "speed": 1.0,  "reward": 20}  # Timeout
}

# [Health, FireInterval, PlantCooldown, Damage, IsCooldown(internal), LastPlantTime(internal), Cost, Type]
# Added name and desc
PLANT_STATS = [
    {"name": "VS Code", "desc": "Standard code emitter", "hp": 200, "fire_rate": 1200, "cooldown": 5000, "damage": 18, "cost": 160, "type": "str"},  # 0: VSCode
    {"name": "PyCharm", "desc": "Reliable Python IDE", "hp": 150, "fire_rate": 1300, "cooldown": 8000, "damage": 18, "cost": 140, "type": "str"},  # 1: Pycharm
    {"name": "WebStorm", "desc": "JS Powerhouse", "hp": 160, "fire_rate": 1300, "cooldown": 8000, "damage": 20, "cost": 140, "type": "str"},  # 2: Webstorm
    {"name": "PHPStorm", "desc": "Solid PHP tool", "hp": 220, "fire_rate": 1500, "cooldown": 8000, "damage": 18, "cost": 150, "type": "str"},  # 3: PHPStorm
    {"name": "CLion", "desc": "C/C++ Expert", "hp": 350, "fire_rate": 1300, "cooldown": 10000,"damage": 12, "cost": 200, "type": "str"},  # 4: Clion
    {"name": "IntelliJ", "desc": "Java High-Arc Thrower", "hp": 300, "fire_rate": 1200, "cooldown": 15000,"damage": 25, "cost": 350, "type": "thr"},  # 5: IntelliJ IDEA
    {"name": "GCC", "desc": "GNU Compiler (Thrower)", "hp": 250, "fire_rate": 1600, "cooldown": 12000,"damage": 28, "cost": 300, "type": "thr"},  # 6: GCC
    {"name": "Python", "desc": "Lightweight Script", "hp": 120, "fire_rate": 1000, "cooldown": 6000, "damage": 15, "cost": 120, "type": "str"},  # 7: CPython
    {"name": "Rustc", "desc": "Safe & Fast", "hp": 280, "fire_rate": 1200, "cooldown": 10000,"damage": 15, "cost": 220, "type": "str"},  # 8: rustc
    {"name": "Node.js", "desc": "Async IO (Fast Fire)", "hp": 160, "fire_rate": 700,  "cooldown": 8000, "damage": 12, "cost": 180, "type": "str"},  # 9: Node.js
    {"name": "Clang", "desc": "LLVM Frontend", "hp": 180, "fire_rate": 1200, "cooldown": 10000,"damage": 25, "cost": 280, "type": "str"},  # 10: Clang
    {"name": "HTML", "desc": "Structure Block (Wall)", "hp": 500, "fire_rate": 1100, "cooldown": 3000, "damage": 0,  "cost": 90,  "type": "sur"},  # 11: HTML (Wall)
    {"name": "JS", "desc": "Dynamic Script", "hp": 150, "fire_rate": 1200, "cooldown": 7000, "damage": 18, "cost": 150, "type": "str"},  # 12: JavaScript
    {"name": "DevC++", "desc": "Heavy Striker", "hp": 100,  "fire_rate": 1500, "cooldown": 5000, "damage": 60, "cost": 80,  "type": "str"},  # 13: DevC++ (Normal Shooter now)
    {"name": "GitHub", "desc": "Open Source (Generates $)", "hp": 50,  "fire_rate": 5000, "cooldown": 10000,"damage": 0,  "cost": 250, "type": "eco"},  # 14: Github (Sun/Money?)
    {"name": "Git", "desc": "Version Control", "hp": 100, "fire_rate": 2000, "cooldown": 10000,"damage": 20, "cost": 170, "type": "spe"}   # 15: Git
]

# --- Asset Manager ---
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
                # Create a transparent placeholder instead of a red square to avoid UI obstructions
                surf = pygame.Surface((50, 50), pygame.SRCALPHA)
                surf.fill((0, 0, 0, 0)) # Ensure fully transparent
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
        # UI
        self.load_image("bg_main", "resource/UI/MAINPAGE/main_page_background.jpg")
        self.load_image("bg_game1", "resource/UI/GAMING/gaming.jpg")
        self.load_image("bg_game2", "resource/UI/GAMING/gaming2.jpg")
        self.load_image("bg_credits", "resource/UI/CREDITS/CREDITS1.jpg") # Level Select BG
        self.load_image("bg_archive", "resource/UI/ARCHIVE/ARCHIVE 首页.png")
        self.load_image("archive_help_1", "resource/UI/ARCHIVE/ARCHIVE 帮助01.png")
        self.load_image("archive_help_2", "resource/UI/ARCHIVE/ARCHIVE 帮助02.png")
        # Archive galleries
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

        # Sounds
        self.load_sound("bgm", "resource/sounds/bgm.wav")
        self.load_sound("start", "resource/sounds/start.wav")
        self.load_sound("error", "resource/sounds/error.wav")
        self.load_sound("error1", "resource/sounds/error1.wav")
        self.load_sound("set", "resource/sounds/set.wav")
        self.load_sound("remove", "resource/sounds/remove.wav")
        self.load_sound("win", "resource/sounds/win.wav")
        
        # UI overlays
        self.load_image("hl_start", "resource/UI/MAINPAGE/main_page_background_start_highlight.jpg")
        self.load_image("hl_save", "resource/UI/MAINPAGE/main_page_background_archive_highlight.jpg")
        self.load_image("hl_quit", "resource/UI/MAINPAGE/main_page_background_quit_highlight.jpg")
        self.load_image("hl_credits", "resource/UI/MAINPAGE/main_page_background_credits_highlight.jpg")
        self.load_image("select_overlay", "resource/UI/CREDITS/CHOOSEIDE1.png")
        self.load_image("level_hover", "resource/UI/CREDITS/BACKGROUND.png")
        
        # Aids
        self.load_image("cleaner", "resource/aids/cleaner.png")
        self.load_image("hidden", "resource/aids/hidden.png")
        self.load_image("no_money", "resource/aids/no_money.png")

        # Plants (1-16)
        for i in range(1, 17):
            self.load_image(f"idle_{i}", f"resource/idle_org/idle_{i}.png")
            self.load_image(f"idle_{i}withcost", f"resource/idle_org/idle_{i}withcost.png")
            
        # Bullets (1-16)
        for i in range(1, 17):
            # Special case for 6 and 7 in original code, but we'll stick to simple mapping for rewrite or try to match
            # Original code loaded lists for 6 and 7. I will load base images.
            if i == 6:
                self.load_image(f"bullet_{i}", "resource/bullet_org/bullet_up.png") # Simplification
            elif i == 7:
                self.load_image(f"bullet_{i}", "resource/bullet_org/bullet_7.png")
            else:
                self.load_image(f"bullet_{i}", f"resource/bullet_org/bullet_{i}.png")
                
        # Enemies (1-10)
        for i in range(1, 11):
            self.load_image(f"enemy_{i}", f"resource/enemy_org/enemy_{i}.png")
            
        # --- Diagnostic Check ---
        # Check for potentially problematic asset files (like red placeholders)
        # This runs once at startup to help debug
        print("--- Asset Integrity Check ---")
        suspect_red_block_files = ["resource/bullet_org/bullet_12.png"] # HTML bullet
        for f in suspect_red_block_files:
            if os.path.exists(f):
                print(f"Note: {f} exists. If this image is red, it causes the red block issue.")
            else:
                print(f"Note: {f} is missing. Transparent placeholder used.")
        print("-----------------------------")

        self.fonts['default'] = pygame.font.SysFont("SimHei", 24)
        self.fonts['title'] = pygame.font.SysFont("Arial", 48)
        self.fonts['warning'] = pygame.font.SysFont("Arial", 120)

R = ResourceManager()

# --- Utility Classes ---

class SaveManager:
    @staticmethod
    def load():
        default_data = {"unlocked": {"1": 1, "2": 0}, "keep_progress": True} # Default keep_progress true for convenience now
        if not os.path.exists(SAVE_PATH):
            return default_data
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Validation
                if "unlocked" not in data: data["unlocked"] = {}
                data["unlocked"].setdefault("1", 1)
                data["unlocked"].setdefault("2", 0)
                return data
        except:
            return default_data

    @staticmethod
    def save(data):
        try:
            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Save failed: {e}")

class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# --- Game Entities ---

class Plant(Sprite):
    def __init__(self, p_id, grid_pos):
        # grid_pos is (row, col)
        row, col = grid_pos
        x = GRID_START_X + col * CELL_WIDTH - 55
        y = GRID_START_Y + row * CELL_HEIGHT - 55
        
        # Original offset correction: grid centers were calculated, plants drawn slightly offset
        # Original: plant_point_center[i][j][0] - 55
        
        img = R.get_image(f"idle_{p_id+1}")
        super().__init__(img, x, y)
        
        stats = PLANT_STATS[p_id]
        self.id = p_id
        self.hp = stats["hp"]
        self.max_hp = stats["hp"]
        self.damage = stats["damage"]
        self.fire_rate = stats["fire_rate"]
        self.type = stats["type"]
        self.row = row
        self.col = col
        self.last_fire = pygame.time.get_ticks()

    def update(self, current_time, enemies, bullets_group, game_ref=None):
        # Shooting Logic
        if self.type == "eco":
            # Economy Logic
            if current_time - self.last_fire > self.fire_rate:
                self.last_fire = current_time
                if game_ref: game_ref.money += 25
            return
        
        # DevC++ exp logic removed, now standard shooter

        if self.type == "spe" or self.type == "sur": return # Specials and Walls (HTML) do not shoot

        # Check if enemy in lane
        lane_enemies = [e for e in enemies if e.row == self.row and e.rect.x > self.rect.x and e.rect.x < SCREEN_WIDTH]
        if not lane_enemies: return

        # Target targeting
        lane_enemies.sort(key=lambda e: e.rect.x)
        target = lane_enemies[0]

        if current_time - self.last_fire > self.fire_rate:
            self.last_fire = current_time
            self.fire(bullets_group, target)

    def fire(self, bullets_group, target=None):
        bx = self.rect.centerx + 20
        by = self.rect.centery - 35  # raise bullet spawn further by 5px
        # Correction based on type
        if self.type == "thr":
            bx -= 20
            by -= 40
        
        img_key = f"bullet_{self.id+1}"
        b_img = R.get_image(img_key)
        
        # Thrower logic uses 'thr' type, others 'str'
        bullet = Bullet(b_img, bx, by, self.damage, self.row, self.type, target)
        bullets_group.add(bullet)

class Bullet(Sprite):
    def __init__(self, image, x, y, damage, row, b_type, target=None):
        super().__init__(image, x, y)
        self.damage = damage
        self.row = row
        self.b_type = b_type
        self.speed = 10
        
        # Physics for parabola
        self.vy = 0
        self.gravity = 0.45 # Reduced gravity for lower arc (25% lower)
        self.start_y = y

        if b_type == "thr":
            self.speed = 8 # Slower horizontal for better arc look
            if target:
                # Calculate trajectory to land on target
                tx = target.rect.centerx + random.randint(-20, 20) # Slight spread
                dist = tx - x
                if dist > 0:
                    t = dist / self.speed
                    # We want to land roughly at the same Y level (enemy feet/center)
                    # 0 = vy*t + 0.5*g*t^2  => vy = -0.5*g*t
                    self.vy = -0.5 * self.gravity * t
            else:
                 # Default arc if no target provided (shouldn't happen with new logic)
                 self.vy = -10

    def update(self):
        if self.b_type == "str":
            self.rect.x += self.speed
        elif self.b_type == "thr":
            self.rect.x += self.speed
            self.rect.y += self.vy
            self.vy += self.gravity
            
            # Ground limit (visual cleanup)
            if self.rect.y > self.start_y + 100:
                self.kill()
        
        if self.rect.x > SCREEN_WIDTH:
            self.kill()

class Enemy(Sprite):
    def __init__(self, e_id, row):
        self.stats = ENEMY_STATS[e_id]
        img = R.get_image(f"enemy_{e_id+1}")
        
        # Initial Position: Right side, aligned to row
        # Row Y center
        center_y = GRID_START_Y + row * CELL_HEIGHT
        x = SCREEN_WIDTH
        y = center_y - 55 # Approx offset to align feet
        
        super().__init__(img, x, y)
        
        self.id = e_id
        self.hp = self.stats["hp"]
        self.speed = self.stats["speed"]
        self.reward = self.stats["reward"]
        self.damage_per_frame = 0.5 # constant?
        self.row = row
        self.is_attacking = False
        self.target_plant = None
        self.frozen = False

    def update(self, plants_group):
        if self.frozen: return

        # Check collision with plants
        # Simple collision
        hit_plants = pygame.sprite.spritecollide(self, plants_group, False)
        
        # Filter for same row and close enough
        target = None
        for p in hit_plants:
            if p.row == self.row:
                # Check distance (touching)
                if self.rect.right > p.rect.left + 20: # Overlap a bit
                    target = p
                    break
        
        if target:
            self.is_attacking = True
            self.target_plant = target
            target.hp -= self.damage_per_frame
            if target.hp <= 0:
                target.kill()
                self.is_attacking = False
        else:
            self.is_attacking = False
        
        if not self.is_attacking:
            self.rect.x -= self.speed
        
        # Lose condition checked by Game manager

# --- Wave System (Adapted) ---
class WaveManager:
    def __init__(self, level_data, difficulty_factor=1.0):
        self.difficulty = max(0.5, difficulty_factor)
        self.waves = self._make_plan()
        self.current_wave_idx = 0
        self.spawned_in_wave = 0
        self.next_spawn_time = 0
        self.finished_spawning = False
        self.wave_gap_end = 0
        self.waiting_wave_gap = False
        self.level_start_time = 0 # Set when game actually starts (post countdown)

        # Track total spawned for a reliable win condition
        self.total_spawned = 0

        # Totals
        self.total_enemies = sum(w['total'] for w in self.waves)
        self.killed_count = 0

    def _make_plan(self):
        df = self.difficulty
        # Base totals ramped by difficulty
        base_totals = [10, 14, 18]
        totals = [max(1, int(t * df)) for t in base_totals]
        # Spawn gaps tighten slightly with difficulty
        base_gaps = [2200, 1800, 1600]
        gaps = [max(800, int(g / (0.9 + 0.1 * df))) for g in base_gaps]
        # Wave pauses shrink with difficulty
        wave_gaps = [max(0, int((3.0 - 0.6 * df) * 1000)), max(0, int((2.0 - 0.5 * df) * 1000)), 0]
        batches = [4, 4, 5]

        waves = []
        for i in range(3):
            waves.append({
                "name": f"wave{i+1}",
                "total": totals[i],
                "gap": gaps[i],
                "wave_gap": wave_gaps[i],
                "batch": batches[i]
            })
        return waves
    
    def update(self, current_time):
        spawns = []
        if self.finished_spawning: return spawns
        
        # Initial delay handled by Game class (30s countdown), WaveManager assumes 'start' has happened
        
        if self.waiting_wave_gap:
            if current_time >= self.wave_gap_end:
                self.waiting_wave_gap = False
                self.current_wave_idx += 1
                self.spawned_in_wave = 0
                if self.current_wave_idx >= len(self.waves):
                    self.finished_spawning = True
            else:
                return spawns

        if self.current_wave_idx >= len(self.waves):
            self.finished_spawning = True
            return spawns

        wave = self.waves[self.current_wave_idx]
        
        if self.spawned_in_wave >= wave["total"]:
            self.waiting_wave_gap = True
            self.wave_gap_end = current_time + wave["wave_gap"]
            return spawns

        if current_time >= self.next_spawn_time:
            # Spawn logic
            batch_size = min(wave["batch"], wave["total"] - self.spawned_in_wave)
            if batch_size > 0:
                count = random.randint(1, batch_size) # Randomize batch slightly
                for _ in range(count):
                    # Simple Tier Logic for rewrite
                    e_id = self._pick_enemy_type(self.current_wave_idx + 1)
                    row = random.randint(0, 4)
                    spawns.append((e_id, row))
                    self.spawned_in_wave += 1
                    self.total_spawned += 1
                    # If this is the last wave and we've spawned everything, mark finished immediately
                    if self.current_wave_idx == len(self.waves) - 1 and self.spawned_in_wave >= wave["total"]:
                        self.finished_spawning = True
                        return spawns
                
                self.next_spawn_time = current_time + wave["gap"]
        
        return spawns

    def _pick_enemy_type(self, wave_num):
        # Simplified probability
        # Tier Map: 1:[0,1], 2:[4,9], 3:[2,8], 4:[3,6], 5:[7,5]
        # Wave 1: Tier 1
        # Wave 2: Mix
        # Wave 3: Harder
        pool = []
        if wave_num == 1:
            pool = [0, 1]
        elif wave_num == 2:
            pool = [0, 1, 4, 9, 2, 8]
        else:
            pool = [0, 1, 4, 9, 2, 8, 3, 6, 7, 5]
        return random.choice(pool)

# --- Difficulty helpers ---
def compute_level_difficulty(level):
    """Return a smooth difficulty scalar based on level meta."""
    # Base keeps early levels gentle; d provides intra-chapter ramp; theme bumps later chapters.
    base = 0.85
    diff = base + level.get("d", 0) * 0.9
    theme = max(1, level.get("theme", 1))
    if theme > 1:
        diff += 0.3 * (theme - 1)
    return max(0.6, min(2.0, diff))

def starting_money_for_level(level):
    """Scale opening money inversely to difficulty so early maps are forgiving."""
    diff = compute_level_difficulty(level)
    base = 3200
    scaled = int(base + 600 * (1.1 - diff))
    return max(2000, min(3800, scaled))

# --- Main Game Application ---

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
        # Mixer channels
        self.sfx_channel = pygame.mixer.Channel(6)
        self.sfx_channel.set_volume(1.0)
        self.lose_sound_channel = pygame.mixer.Channel(7)
        self.lose_sound_channel.set_volume(1.0)
        # Start BGM loop
        try:
            pygame.mixer.music.load(resource_path("resource/sounds/bgm.wav"))
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"BGM load/play failed: {e}")
        self.save_data = SaveManager.load()
        
        self.state = "MAIN_MENU"
        
        # Level Select Data
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
        
        # Layouts
        self.level_buttons = {}
        y_base_1 = 260
        y_base_2 = 520
        x_start = 180
        box_w, box_h = 200, 90
        gap = 240
        for i in range(5):
            self.level_buttons[f"1-{i+1}"] = pygame.Rect(x_start + i*gap, y_base_1, box_w, box_h)
            self.level_buttons[f"2-{i+1}"] = pygame.Rect(x_start + i*gap, y_base_2, box_w, box_h)

        # Game Session Data
        self.selected_level = None
        self.selected_plants_indices = []
        
        # Gameplay Objects
        self.plants = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.money = 3000
        self.wave_manager = None
        self.game_start_tick = 0
        self.spawn_delay = 30000
        self.warning_time = 25000
        self.win_sound_played = False

        # Input
        self.mouse_cooldown_end = 0  # delay mouse handling after clicks
        self.mouse_block_until = 0   # block mouse across state transitions
        
        # Plant Selection State
        self.plant_select_rects = []
        for r in range(4):
            for c in range(4):
                x = SELECT_START_X + c * SELECT_GAP_X
                y = SELECT_START_Y + r * SELECT_GAP_Y
                self.plant_select_rects.append(pygame.Rect(x, y, 100, 100))
        self.ok_button = pygame.Rect(1350, 780, 150, 80)
        
        # In-Game UI
        self.slot_rects = []
        for i in range(10):
            self.slot_rects.append(pygame.Rect(220 + i*120, 10, 100, 100))
        self.shovel_rect = pygame.Rect(1455, 5, 100, 100)
        self.holding_plant_idx = -1 # -1 None, 0-9 index in selected_plants
        self.holding_shovel = False
        
        # Debug
        self.debug_ups = 0
        self.debug_last = 0
        self.debug_mode = False
        self.last_debug_log = 0
        self.archive_message = ""
        self.archive_mode = "main"
        self.archive_page = 0
        self.credits_page = 0

        # Story gating
        self.story_shown = {"1-1": False, "2-1": False, "final": False}
        self.story_texts = {
            "1-1": "第一章\n你是计算机专业的大学生，正趴在宿舍桌前用VS Code写代码。\n赶ddl的压力让你手忙脚乱，屏幕上堆了一堆没调试完的代码，桌面也乱得全是文件图标。\n突然，屏幕一闪，那些没修好的BUG竟然活了过来，变成一个个黑糊糊的小僵尸，顺着屏幕边缘爬出来，\n开始啃咬你桌面上的文件——再不管，你的作业就要被它们毁完了！",
            "2-1": "第二章\n他们爬进了你的编辑器！！这里藏着你所有的项目代码和作业草稿，要是被它们毁了，整个学期的努力都白费。\n更麻烦的是，编辑器里的BUG僵尸变得更强了...",
            "final": "最终结算\n恭喜你de完了所有bug!你完成了作业沉沉睡去..."
        }
        self.story_after_state = None
        self.story_active_key = None
        self.story_error_timer = None
        self.story_error_played = False

        # Win animation
        self.win_anim_start = None

        # Lose audio sequence
        self.lose_sound_sequence = []
        self.lose_sound_index = 0
        self.lose_sound_channel = pygame.mixer.Channel(7)
        self.lose_sound_active = False

    def run(self):
        while self.running:
            raw_events = pygame.event.get()
            now = pygame.time.get_ticks()

            # Mouse suppression: block after state switches and add 0.1s cooldown after each click
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
            elif self.state == "STORY":
                self.update_story(events)

            # Block mouse briefly after any state change to avoid click-through
            if self.state != state_before:
                self.mouse_block_until = pygame.time.get_ticks() + 200
                
            self.clock.tick(FPS)
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

    def draw_text(self, text, x, y, font_key='default', color=BLACK, center=False):
        font = R.fonts.get(font_key, R.fonts['default'])
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
            self.sfx_channel.stop()  # ensure channel free
            self.sfx_channel.play(snd)
        except Exception:
            snd.play()

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
        # Simple overlay for narrative beats
        self.screen.blit(R.get_image("bg_credits"), (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 230))
        self.screen.blit(overlay, (0, 0))

        text = self.story_texts.get(self.story_active_key, "")

        # Typewriter effect
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
            self.draw_text(line, 180, y, 'default', BLACK)
            y += 70

        if self.story_active_key != "final":
            self.draw_text("按任意键继续", 750, 820, 'default', BLACK)

        for e in events:
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                self.story_active_key = None
                next_state = self.story_after_state or "LEVEL_SELECT"
                self.story_after_state = None
                self.story_start_time = None
                self.state = next_state
                return

            # Timed error sound for first chapter story
            if self.story_active_key == "1-1" and self.story_error_timer:
                now = pygame.time.get_ticks()
                if not self.story_error_played and now >= self.story_error_timer:
                    self.play_sfx("error", 1.0)
                    self.story_error_played = True

    # --- STATES ---

    def update_main_menu(self, events):
        self.screen.blit(R.get_image("bg_main"), (0, 0))
        mx, my = pygame.mouse.get_pos()
        
        # Buttons areas (approx based on original)
        btn_start = pygame.Rect(90, 310, 350, 100)
        btn_load = pygame.Rect(95, 450, 425, 95)
        btn_quit = pygame.Rect(95, 590, 515, 85)
        btn_credits = pygame.Rect(95, 740, 405, 85)
        
        if btn_start.collidepoint(mx, my):
            self.screen.blit(R.get_image("hl_start"), (0,0))
            if self.mouse_ready() and pygame.mouse.get_pressed()[0]: self.state = "LEVEL_SELECT"
        elif btn_load.collidepoint(mx, my):
            self.screen.blit(R.get_image("hl_save"), (0,0))
            if self.mouse_ready() and pygame.mouse.get_pressed()[0]:
                self.archive_mode = "main"
                self.archive_message = ""
                self.state = "ARCHIVE"
        elif btn_quit.collidepoint(mx, my):
            self.screen.blit(R.get_image("hl_quit"), (0,0))
            if self.mouse_ready() and pygame.mouse.get_pressed()[0]: self.running = False
        elif btn_credits.collidepoint(mx, my):
             self.screen.blit(R.get_image("hl_credits"), (0,0))
             if self.mouse_ready() and pygame.mouse.get_pressed()[0]:
                 self.credits_page = 0
                 self.state = "CREDITS"

        # Event handling for clicks specifically if needed, but polling above works for simple UI

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
            if not rect: continue
            
            # Check unlock status
            theme = str(lvl["theme"])
            idx = int(lid.split("-")[1])
            unlocked_upto = self.save_data["unlocked"].get(theme, 1)
            is_unlocked = self.debug_mode or idx <= unlocked_upto
            
            # Draw Frame
            pygame.draw.rect(self.screen, (30,30,30), rect, 2)
            
            # Draw Text
            self.draw_text(lid, rect.x + 20, rect.y + 30, 'default', BLACK)
            
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
                # Shade
                shade = pygame.Surface((200, 90))
                shade.fill(BLACK)
                shade.set_alpha(150)
                self.screen.blit(shade, rect)
        
        # ESC to Menu
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = "MAIN_MENU"

    def update_plant_select(self, events):
        # Draw Background - User requested decoration/background
        # Using level select background as base + translucent overlay
        self.screen.blit(R.get_image("bg_credits"), (0,0))
        
        # Overlay for content area
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 220)) # White with high opacity
        self.screen.blit(overlay, (0,0))
        
        # Decorative Big Frame for Plants
        panel_rect = pygame.Rect(SELECT_START_X - 30, SELECT_START_Y - 30, 
                     SELECT_GAP_X * 3 + SELECT_SLOT_SIZE + 60, 
                     SELECT_GAP_Y * 3 + SELECT_SLOT_SIZE + 100) # Extended downwards
        pygame.draw.rect(self.screen, (50, 50, 50), panel_rect, 5, border_radius=15)
        # Title (shifted down 15px)
        self.draw_text("CHOOSE YOUR IDES", panel_rect.centerx - 230, panel_rect.top - 45, 'title', BLACK)
        
        mx, my = pygame.mouse.get_pos()
        hovered_plant_idx = -1
        
        # Draw selectable plants
        available = [i for i in range(16) if i not in self.selected_plants_indices]
        
        for idx in range(16):
            if idx in self.selected_plants_indices: continue
            
            slot_rect = self.plant_select_rects[idx]
            
            # Draw Slot Frame - More decorative
            pygame.draw.rect(self.screen, (200, 200, 200), slot_rect, border_radius=5) # Light gray fill
            pygame.draw.rect(self.screen, (80, 80, 80), slot_rect, 2, border_radius=5) # Dark gray border

            # Draw plant
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
        
        # Draw selected list at top
        for i, p_idx in enumerate(self.selected_plants_indices):
            # Draw slot frame first (shifted down with title)
            x, y = 100 + i*110, 75
            sel_rect = pygame.Rect(x, y, 90, 90)
            
            pygame.draw.rect(self.screen, (230, 230, 255), sel_rect, border_radius=5)
            pygame.draw.rect(self.screen, BLACK, sel_rect, 2, border_radius=5)

            img = R.get_image(f"idle_{p_idx+1}withcost")
            # Center image in 90x90 slot
            ir = img.get_rect(center=sel_rect.center)
            self.screen.blit(img, ir)
            
            # Check hover on selected bar for removal (optional enhancement, but good for UX)
            if sel_rect.collidepoint(mx, my):
                 pygame.draw.rect(self.screen, RED, sel_rect, 3, border_radius=5)
                 for e in events:
                     if e.type == pygame.MOUSEBUTTONUP:
                         self.selected_plants_indices.pop(i)
                         # Break to avoid index error
                         break

        # Draw OK Button
        pygame.draw.rect(self.screen, BLACK, self.ok_button, 3)
        self.draw_text("OK!!", self.ok_button.x + 30, self.ok_button.y + 20, 'default', BLACK)
        
        if self.ok_button.collidepoint(mx, my):
             pygame.draw.rect(self.screen, HOVER_COLOR, self.ok_button, 3)
             for e in events:
                 if e.type == pygame.MOUSEBUTTONUP and len(self.selected_plants_indices) > 0:
                     self.start_game()

        # Draw Tooltip
        if hovered_plant_idx != -1:
            stats = PLANT_STATS[hovered_plant_idx]
            tip_w, tip_h = 300, 120
            tip_x = mx + 15
            tip_y = my + 15
            # Clamp to screen
            if tip_x + tip_w > SCREEN_WIDTH: tip_x = mx - tip_w - 15
            if tip_y + tip_h > SCREEN_HEIGHT: tip_y = my - tip_h - 15
            
            # Background
            pygame.draw.rect(self.screen, (240, 240, 240), (tip_x, tip_y, tip_w, tip_h))
            pygame.draw.rect(self.screen, BLACK, (tip_x, tip_y, tip_w, tip_h), 2)
            
            # Text
            self.draw_text(stats["name"], tip_x + 10, tip_y + 10, 'default', BLACK)
            self.draw_text(f"Cost: {stats['cost']}", tip_x + 10, tip_y + 40, 'default', BLACK)
            self.draw_text(f"HP: {stats['hp']} Dmg: {stats['damage']}", tip_x + 10, tip_y + 65, 'default', BLACK)
            self.draw_text(stats["desc"], tip_x + 10, tip_y + 90, 'default', (50, 50, 50))

        # ESC to return to level select
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
        self.game_start_tick = pygame.time.get_ticks()
        self.enemies_killed = 0 # Track kills for win condition
        self.win_sound_played = False
        
        # Init Plant Cooldowns
        self.plant_cd_status = {} # {idx: last_plant_time}
        for idx in self.selected_plants_indices:
            self.plant_cd_status[idx] = -99999

    def update_gaming(self, events):
        now = pygame.time.get_ticks()
        elapsed = now - self.game_start_tick
        
        # Screen Clearing: Must clear the screen to prevent "smearing" artifacts (red blocks/trails)
        self.screen.fill(BLACK) 
        
        bg = R.get_image("bg_game2") if self.selected_level["theme"] == 2 else R.get_image("bg_game1")
        self.screen.blit(bg, (0,0))
        
        # --- Update Logic ---
        
        # Spawning
        if elapsed > self.spawn_delay:
            spawns = self.wave_manager.update(now)
            for (e_id, row) in spawns:
                self.enemies.add(Enemy(e_id, row))
        
        # Money
        if now % 1000 < 20: 
            pass 
        
        # Entities
        self.plants.update(now, self.enemies, self.bullets, game_ref=self)
        self.bullets.update()
        self.enemies.update(self.plants)
        
        # Collisions: Bullets hitting Enemies
        # Assuming single hit per bullet for now unless penetration
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

        # Cleanup any enemies that dropped to <=0 HP outside collision loop
        for enemy in list(self.enemies):
            if enemy.hp <= 0 and enemy.alive():
                enemy.kill()
                self.money += enemy.reward
                self.enemies_killed += 1
        
                # Win Condition - Ultra simple: spawning done + no enemies on screen
        if self.wave_manager:
            spawning_done = self.wave_manager.finished_spawning

            # If spawning is done, clean up enemies that haven't entered the screen yet
            if spawning_done:
                for e in list(self.enemies):
                    if e.rect.x >= SCREEN_WIDTH:  # Still at spawn point or off-screen right
                        e.kill()

            alive = len(self.enemies)

            if self.debug_mode:
                if now - self.last_debug_log > 1000:
                    self.last_debug_log = now
                    print(f"DEBUG WIN CHECK -> alive: {alive}, spawning_done: {spawning_done}")
                    # Print positions of remaining enemies
                    for e in self.enemies:
                        print(f"  Enemy id={e.id} row={e.row} x={e.rect.x} hp={e.hp} frozen={e.frozen}")
                self.draw_text(f"Alive: {alive} | Spawning Done: {spawning_done}", 20, 210, 'default', BLACK)

            # Win: all waves finished spawning AND no enemies left on screen
            if spawning_done and alive == 0:
                if self.selected_level and self.selected_level.get("final") and not self.story_shown["final"]:
                    self.start_story("final", "WIN")
                else:
                    self.play_sfx("win", 1.0)
                    self.state = "WIN"
                return
        
        # Failsafe: Cleanup enemies that are way off-screen (left or right)
        for e in list(self.enemies):
            # Clean up enemies stuck far right (never entered) or far left
            if e.rect.x > SCREEN_WIDTH + 200 or e.rect.x < -200:
                e.kill()
            # Also clean up any with hp <= 0 that somehow survived
            elif e.hp <= 0:
                e.kill()
            
        # Lose Condition
        for e in self.enemies:
            if e.rect.x < 200: # House limit
                self.state = "LOSE"
                # Prepare lose sound sequence
                self.lose_sound_sequence = ["error1"] * 5 + ["error"]
                self.lose_sound_index = 0
                self.lose_sound_active = True
                if self.lose_sound_channel: self.lose_sound_channel.stop()
                return

        # --- Draw UI ---
        
        # Slot Bar
        self.draw_text(str(self.money), 90, 100, 'default', BLACK)
        
        mx, my = pygame.mouse.get_pos()
        
        # Slots
        for i, slot_rect in enumerate(self.slot_rects):
            if i >= len(self.selected_plants_indices): break
            p_idx = self.selected_plants_indices[i]
            img = R.get_image(f"idle_{p_idx+1}withcost")
            self.screen.blit(img, slot_rect.topleft)
            
            # Cooldown Mask
            stats = PLANT_STATS[p_idx]
            last_p = self.plant_cd_status.get(p_idx, 0)
            cd_remain = stats["cooldown"] - (now - last_p)
            if cd_remain > 0:
                ratio = cd_remain / stats["cooldown"]
                h = int(100 * ratio)
                mask = pygame.Surface((100, h))
                mask.fill(BLACK)
                mask.set_alpha(150)
                self.screen.blit(mask, (slot_rect.x, slot_rect.y + (100-h)))
            
            # Cost check
            if self.money < stats["cost"]:
                self.screen.blit(R.get_image("no_money"), (slot_rect.x, slot_rect.y - 10))

            # Interaction
            if slot_rect.collidepoint(mx, my):
                if self.mouse_ready() and pygame.mouse.get_pressed()[0] and not self.holding_shovel:
                    if cd_remain <= 0 and self.money >= stats["cost"]:
                        self.holding_plant_idx = i

        # Shovel
        self.screen.blit(R.get_image("cleaner"), self.shovel_rect)
        if self.shovel_rect.collidepoint(mx, my):
               if self.mouse_ready() and pygame.mouse.get_pressed()[0]:
                 self.holding_shovel = True
                 self.holding_plant_idx = -1

        # Handling inputs for placing
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3: # Right click cancel
                self.holding_plant_idx = -1
                self.holding_shovel = False
            
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # Place Plant or Shovel
                # Detect grid click
                c = (mx - GRID_START_X) // CELL_WIDTH
                r = (my - GRID_START_Y) // CELL_HEIGHT
                
                if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                    if self.holding_shovel:
                        # Find plant at r,c and kill
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
                        # Check empty
                        occupied = any(p.row == r and p.col == c for p in self.plants)
                        if not occupied:
                            p_idx = self.selected_plants_indices[self.holding_plant_idx]
                            stats = PLANT_STATS[p_idx]
                            self.money -= stats["cost"]
                            self.plants.add(Plant(p_idx, (r,c)))
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

        # --- Draw Game Entities ---
        self.plants.draw(self.screen)
        self.enemies.draw(self.screen)
        self.bullets.draw(self.screen)

        # Warning (Drawn on top of entities)
        if self.warning_time < elapsed < self.spawn_delay:
            if (elapsed // 200) % 2 == 0:
                txt = "YOUR BUGS ARE COMING!!!"
                # Adjusted size and pos
                font = R.fonts.get('warning', pygame.font.SysFont(None, 120))
                surf = font.render(txt, True, RED)
                rect = surf.get_rect(center=(800, 280))
                self.screen.blit(surf, rect)

        # Mouse Follower
        if self.holding_plant_idx != -1:
               p_idx = self.selected_plants_indices[self.holding_plant_idx]
               img = R.get_image(f"idle_{p_idx+1}withcost")
               self.screen.blit(img, (mx-50, my-50))
        elif self.holding_shovel:
             self.screen.blit(R.get_image("cleaner"), (mx-50, my-50))


    def update_pause(self, events):
        # Draw overlay
        # Darken screen first
        darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        darkness.fill(BLACK)
        darkness.set_alpha(150)
        self.screen.blit(darkness, (0,0))

        # Center the pause image
        p_img = R.get_image("bg_pause")
        p_rect = p_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(p_img, p_rect)
        
        # Determine pause start time only once
        if not hasattr(self, 'pause_start_ts'):
            self.pause_start_ts = pygame.time.get_ticks()

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    self.state = "GAMING"
                    # Adjust start time to account for pause duration
                    pause_duration = pygame.time.get_ticks() - self.pause_start_ts
                    self.game_start_tick += pause_duration
                    # Also shift cooldowns
                    for idx in self.plant_cd_status:
                        self.plant_cd_status[idx] += pause_duration
                    # Reset pause timestamp for next time
                    delattr(self, 'pause_start_ts')
                elif e.key == pygame.K_ESCAPE:
                    self.state = "MAIN_MENU"
                    if hasattr(self, 'pause_start_ts'): delattr(self, 'pause_start_ts')

    def update_win(self, events):
        if self.selected_level.get("final") and not getattr(self, "win_sound_played", False):
            self.play_sfx("win", 1.0)
            self.win_sound_played = True
        if self.selected_level["final"]:
            # Animated scale-in for final win image
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
            rect = scaled.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(scaled, rect)
            self.draw_text("按任意键返回选关", 650, 820, 'default', BLACK)
        else:
            # Standalone text without bg image - just overlay on current screen or black
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(WHITE)
            overlay.set_alpha(100) # Semi-transparent white to fade out game
            self.screen.blit(overlay, (0,0))
            
            self.draw_text("YOU WIN!", 800, 450, 'warning', BLACK, True)
             
        # Unlock logic (Only once)
        if self.selected_level:
            theme = str(self.selected_level["theme"])
            lid = int(self.selected_level["id"].split("-")[1])
            if lid < 5:
                # Linear progression: unlock next in theme
                curr = self.save_data["unlocked"].get(theme, 1)
                if lid >= curr:
                    self.save_data["unlocked"][theme] = lid + 1
                    SaveManager.save(self.save_data)
            elif lid == 5 and theme == "1":
                 # Unlock Theme 2?
                 if self.save_data["unlocked"].get("2", 0) == 0:
                     self.save_data["unlocked"]["2"] = 1
                     SaveManager.save(self.save_data)
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN or e.type == pygame.KEYDOWN:
                self.win_anim_start = None
                self.state = "LEVEL_SELECT"

    def update_lose(self, events):
        # Darken bg
        darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        darkness.fill(BLACK)
        darkness.set_alpha(150)
        self.screen.blit(darkness, (0,0))

        # Center Lose Image
        l_img = R.get_image("img_lose")
        l_rect = l_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(l_img, l_rect)
        
        # Center Return Button
        r_img = R.get_image("img_return")
        r_rect = r_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
        self.screen.blit(r_img, r_rect)

        # Sequential lose sound playback
        if self.lose_sound_active and self.lose_sound_index < len(self.lose_sound_sequence):
            if not self.lose_sound_channel.get_busy():
                key = self.lose_sound_sequence[self.lose_sound_index]
                # Stop channel to avoid overlap then play
                self.sfx_channel.stop()
                self.play_sfx(key, 1.0)
                self.lose_sound_index += 1
            # when finished queue
            if self.lose_sound_index >= len(self.lose_sound_sequence) and not self.lose_sound_channel.get_busy():
                self.lose_sound_active = False
        
        for e in events:
             if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                 self.state = "LEVEL_SELECT"

    def update_credits(self, events):
        # Clear to avoid leftover visuals from previous state
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

        # Page indicator top-right
        self.draw_text(f"{(self.credits_page % 4) + 1}/4", SCREEN_WIDTH - 80, 20, 'default', BLACK)

    def update_archive(self, events):
        # Subpages: tips / ide / bug
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

            # Page indicator
            self.draw_text(f"{self.archive_page + 1}/{len(keys)}", 1550, 20, 'default', BLACK)
            return

        # Main archive page
        self.screen.blit(R.get_image("bg_archive"), (0, 0))

        mx, my = pygame.mouse.get_pos()
        for btn in ARCHIVE_BUTTONS:
            area_rect = pygame.Rect(btn["pos"][0], btn["pos"][1], btn["area_size"][0], btn["area_size"][1])

            # Invisible hitbox only; no border/text
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

        # ESC to Main Menu
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = "MAIN_MENU"

if __name__ == "__main__":
    game = Game()
    game.run()
