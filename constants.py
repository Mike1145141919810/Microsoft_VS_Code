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
        "text_size": (327, 63),
    },
    {
        "name": "僵尸BUG图鉴",
        "text": "僵尸BUG图鉴",
        "pos": (620, 250),
        "area_size": (360, 538),
        "text_pos": (620, 750),
        "text_size": (355, 63),
    },
    {
        "name": "游玩提示",
        "text": "游玩提示！",
        "pos": (1130, 250),
        "area_size": (360, 538),
        "text_pos": (1165, 750),
        "text_size": (291, 63),
    },
]

ARCHIVE_HELP_KEYS = ["archive_help_1", "archive_help_2"]
ARCHIVE_IDE_KEYS = [
    "植物page1",
    "植物page2",
    "植物page3",
    "植物page4",
    "植物page5",
    "植物page6",
]
ARCHIVE_BUG_KEYS = [
    "BUGspage1",
    "BUGspage2",
    "BUGspage3",
    "BUGspage4",
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
SELECT_START_Y = 240
SELECT_GAP_X = 170
SELECT_GAP_Y = 125

# Enemy stats
ENEMY_STATS = {
    0: {"hp": 80, "speed": 1.5, "reward": 15},  # Syntax/Compile Error
    1: {"hp": 80, "speed": 2.5, "reward": 20},  # Null Pointer
    2: {"hp": 200, "speed": 1.0, "reward": 25},  # Infinite Loop
    3: {"hp": 300, "speed": 1.0, "reward": 40},  # Memory Overflow
    4: {"hp": 200, "speed": 1.25, "reward": 20},  # Array Index Out
    5: {"hp": 450, "speed": 0.75, "reward": 50},  # Stack Overflow
    6: {"hp": 500, "speed": 0.375, "reward": 10},  # Memory Leak
    7: {"hp": 600, "speed": 0.25, "reward": 80},  # No Idea
    8: {"hp": 300, "speed": 1.0, "reward": 40},  # Missing Runtime
    9: {"hp": 250, "speed": 1.0, "reward": 20},  # Timeout
}

# Plant stats
PLANT_STATS = [
    {"name": "VS Code", "desc": "Standard code emitter", "hp": 200, "fire_rate": 1200, "cooldown": 5000, "damage": 18, "cost": 160, "type": "str"},
    {"name": "PyCharm", "desc": "Reliable Python IDE", "hp": 150, "fire_rate": 1300, "cooldown": 8000, "damage": 18, "cost": 140, "type": "str"},
    {"name": "WebStorm", "desc": "JS Powerhouse", "hp": 160, "fire_rate": 1300, "cooldown": 8000, "damage": 20, "cost": 140, "type": "str"},
    {"name": "PHPStorm", "desc": "Solid PHP tool", "hp": 220, "fire_rate": 1500, "cooldown": 8000, "damage": 18, "cost": 150, "type": "str"},
    {"name": "CLion", "desc": "C/C++ Expert", "hp": 350, "fire_rate": 1300, "cooldown": 10000, "damage": 12, "cost": 200, "type": "str"},
    {"name": "IntelliJ", "desc": "Java High-Arc Thrower", "hp": 300, "fire_rate": 1200, "cooldown": 15000, "damage": 25, "cost": 350, "type": "thr"},
    {"name": "GCC", "desc": "GNU Compiler (Thrower)", "hp": 250, "fire_rate": 1600, "cooldown": 12000, "damage": 28, "cost": 300, "type": "thr"},
    {"name": "Python", "desc": "Lightweight Script", "hp": 120, "fire_rate": 1000, "cooldown": 6000, "damage": 15, "cost": 120, "type": "str"},
    {"name": "Rustc", "desc": "Safe & Fast", "hp": 280, "fire_rate": 1200, "cooldown": 10000, "damage": 15, "cost": 220, "type": "str"},
    {"name": "Node.js", "desc": "Async IO (Fast Fire)", "hp": 160, "fire_rate": 700, "cooldown": 8000, "damage": 12, "cost": 180, "type": "str"},
    {"name": "Clang", "desc": "LLVM Frontend", "hp": 180, "fire_rate": 1200, "cooldown": 10000, "damage": 25, "cost": 280, "type": "str"},
    {"name": "HTML", "desc": "Structure Block (Wall)", "hp": 500, "fire_rate": 1100, "cooldown": 3000, "damage": 0, "cost": 90, "type": "sur"},
    {"name": "JS", "desc": "Dynamic Script", "hp": 150, "fire_rate": 1200, "cooldown": 7000, "damage": 18, "cost": 150, "type": "str"},
    {"name": "DevC++", "desc": "Heavy Striker", "hp": 100, "fire_rate": 1500, "cooldown": 5000, "damage": 60, "cost": 80, "type": "str"},
    {"name": "GitHub", "desc": "Open Source (Generates $)", "hp": 50, "fire_rate": 5000, "cooldown": 10000, "damage": 0, "cost": 250, "type": "eco"},
    {"name": "Git", "desc": "Version Control", "hp": 100, "fire_rate": 2000, "cooldown": 10000, "damage": 20, "cost": 170, "type": "spe"},
]
