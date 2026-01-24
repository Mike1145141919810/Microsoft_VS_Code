import random


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
        self.level_start_time = 0
        self.total_spawned = 0
        self.total_enemies = sum(w["total"] for w in self.waves)
        self.killed_count = 0

    def _make_plan(self):
        df = self.difficulty
        base_totals = [10, 14, 18]
        totals = [max(1, int(t * df)) for t in base_totals]
        base_gaps = [2200, 1800, 1600]
        gaps = [max(800, int(g / (0.9 + 0.1 * df))) for g in base_gaps]
        wave_gaps = [
            max(0, int((3.0 - 0.6 * df) * 1000)),
            max(0, int((2.0 - 0.5 * df) * 1000)),
            0,
        ]
        batches = [4, 4, 5]

        waves = []
        for i in range(3):
            waves.append(
                {
                    "name": f"wave{i+1}",
                    "total": totals[i],
                    "gap": gaps[i],
                    "wave_gap": wave_gaps[i],
                    "batch": batches[i],
                }
            )
        return waves

    def update(self, current_time):
        spawns = []
        if self.finished_spawning:
            return spawns

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
            batch_size = min(wave["batch"], wave["total"] - self.spawned_in_wave)
            if batch_size > 0:
                count = random.randint(1, batch_size)
                for _ in range(count):
                    e_id = self._pick_enemy_type(self.current_wave_idx + 1)
                    row = random.randint(0, 4)
                    spawns.append((e_id, row))
                    self.spawned_in_wave += 1
                    self.total_spawned += 1
                    if self.current_wave_idx == len(self.waves) - 1 and self.spawned_in_wave >= wave["total"]:
                        self.finished_spawning = True
                        return spawns

                self.next_spawn_time = current_time + wave["gap"]

        return spawns

    def _pick_enemy_type(self, wave_num):
        pool = []
        if wave_num == 1:
            pool = [0, 1]
        elif wave_num == 2:
            pool = [0, 1, 4, 9, 2, 8]
        else:
            pool = [0, 1, 4, 9, 2, 8, 3, 6, 7, 5]
        return random.choice(pool)


def compute_level_difficulty(level):
    base = 0.85
    diff = base + level.get("d", 0) * 0.9
    theme = max(1, level.get("theme", 1))
    if theme > 1:
        diff += 0.3 * (theme - 1)
    return max(0.6, min(2.0, diff))


def starting_money_for_level(level):
    diff = compute_level_difficulty(level)
    base = 3200
    scaled = int(base + 600 * (1.1 - diff))
    return max(2000, min(3800, scaled))
