import random


class WaveManager:
    def __init__(self, level_data, difficulty_factor=1.0):
        self.level_data = level_data or {}
        self.level_id = str(self.level_data.get("id", "1-1"))
        self.difficulty = max(0.5, difficulty_factor)
        self.chapter, self.stage = self._parse_level_id(self.level_id)
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

    def _parse_level_id(self, level_id):
        try:
            parts = level_id.split("-")
            chapter = int(parts[0])
            stage = int(parts[1])
            return chapter, stage
        except Exception:
            return 1, 1

    def _make_plan(self):
        df = self.difficulty
        chapter = self.chapter
        stage = self.stage
        final_level = bool(self.level_data.get("final"))

        wave_count = 10

        # 基于关卡编号的基础量和递增量，模仿PVZ“阶数+级别上限”逐波抬升。
        base_total = 6 + (stage - 1) * 1.5 + (chapter - 1) * 3
        growth = 1.1 + 0.2 * df + 0.15 * (chapter - 1) + 0.1 * (stage - 1)

        waves = []
        for w in range(1, wave_count + 1):
            intensity = base_total + growth * (w - 1)

            # 旗帜波（第5、10波）强化；最终关后半程再抬一次。
            if w in (5, 10):
                intensity *= 1.35
            if final_level and w >= 8:
                intensity *= 1.15

            total = max(6, int(intensity * df))
            gap = self._gap_for_wave(w, df, chapter)
            wave_gap = self._wave_gap_after(w)
            batch = self._batch_for_wave(w, chapter)
            weights = self._pool_for_wave(w, chapter, stage, df, final_level)

            waves.append(
                {
                    "name": f"wave{w}",
                    "total": total,
                    "gap": gap,
                    "wave_gap": wave_gap,
                    "batch": batch,
                    "weights": weights,
                }
            )

        return waves

    def _gap_for_wave(self, wave_num, df, chapter):
        base = 1900 - (chapter - 1) * 150 - wave_num * 35
        tuned = int(base / (0.9 + 0.2 * df))
        return max(650, tuned)

    def _wave_gap_after(self, wave_num):
        if wave_num in (5, 10):
            return 3200
        return 2000

    def _batch_for_wave(self, wave_num, chapter):
        if wave_num <= 3:
            return 4
        if wave_num <= 6:
            return 5
        return 6 if chapter > 1 else 5

    def _pool_for_wave(self, wave_num, chapter, stage, df, is_final):
        # 参考PVZ“阶数”解锁：波数越高越容易抽到高阶僵尸。
        if wave_num <= 2:
            weights = {0: 3, 1: 2}
        elif wave_num <= 4:
            weights = {0: 2, 1: 2, 2: 2, 4: 1, 9: 1}
        elif wave_num <= 6:
            weights = {0: 2, 1: 2, 2: 2, 4: 2, 9: 1, 3: 1, 8: 1}
        elif wave_num <= 8:
            weights = {0: 1, 1: 1, 2: 2, 4: 2, 9: 1, 3: 2, 8: 2, 6: 1}
        else:
            weights = {0: 1, 1: 1, 2: 2, 4: 2, 9: 1, 3: 2, 8: 2, 6: 2, 5: 1, 7: 1}

        # 第二章和更高难度：让高阶占比更大。
        heavy_ids = [3, 5, 6, 7, 8]
        scale = 1.0 + 0.25 * (chapter - 1) + 0.2 * max(0.0, df - 1.0)
        for hid in heavy_ids:
            if hid in weights:
                weights[hid] = max(1, int(weights[hid] * scale))

        if is_final and wave_num >= 7:
            for hid in (5, 7):
                if hid in weights:
                    weights[hid] += 1
                else:
                    weights[hid] = 1

        return weights

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
                    e_id = self._pick_enemy_type(wave)
                    row = random.randint(0, 4)
                    spawns.append((e_id, row))
                    self.spawned_in_wave += 1
                    self.total_spawned += 1
                    if self.current_wave_idx == len(self.waves) - 1 and self.spawned_in_wave >= wave["total"]:
                        self.finished_spawning = True
                        return spawns

                self.next_spawn_time = current_time + wave["gap"]

        return spawns

    def _pick_enemy_type(self, wave_def):
        weights = wave_def.get("weights") or {0: 1, 1: 1}
        ids = list(weights.keys())
        probs = list(weights.values())
        return random.choices(ids, weights=probs, k=1)[0]


class EndlessWaveManager:
    def __init__(self, difficulty=1.0):
        self.difficulty = max(0.8, difficulty)
        self.wave_index = 1
        self.spawned_in_wave = 0
        self.next_spawn_time = 0
        self.waiting_wave_gap = False
        self.wave_gap_end = 0
        self.current_wave = self._make_wave(self.wave_index)
        self.wave_started_ts = 0

    def _make_wave(self, wave_num):
        df = self.difficulty
        base_total = 7 + (wave_num - 1) * (1.8 + 0.2 * df)
        total = max(6, int(base_total * (0.9 + 0.15 * df)))
        gap = max(420, int(1700 - wave_num * 40 - df * 80))
        wave_gap = 15000
        batch = min(7, 4 + wave_num // 3)
        weights = self._pool_for_wave(wave_num, df)

        return {
            "name": f"endless_wave{wave_num}",
            "total": total,
            "gap": gap,
            "wave_gap": wave_gap,
            "batch": batch,
            "weights": weights,
        }

    def _pool_for_wave(self, wave_num, df):
        if wave_num <= 2:
            weights = {0: 3, 1: 2}
        elif wave_num <= 4:
            weights = {0: 2, 1: 2, 2: 2, 4: 1, 9: 1}
        elif wave_num <= 6:
            weights = {0: 2, 1: 2, 2: 2, 4: 2, 9: 1, 3: 1, 8: 1}
        elif wave_num <= 8:
            weights = {0: 1, 1: 1, 2: 2, 4: 2, 9: 1, 3: 2, 8: 2, 6: 1}
        else:
            weights = {0: 1, 1: 1, 2: 2, 4: 2, 9: 1, 3: 2, 8: 2, 6: 2, 5: 1, 7: 1}

        heavy_ids = [3, 5, 6, 7, 8]
        scale = 1.0 + 0.2 * max(0.0, df - 1.0) + 0.03 * wave_num
        for hid in heavy_ids:
            if hid in weights:
                weights[hid] = max(1, int(weights[hid] * scale))

        if wave_num >= 10:
            for hid in (5, 7):
                weights[hid] = weights.get(hid, 1) + 1

        return weights

    def update(self, current_time):
        spawns = []
        if not self.wave_started_ts:
            self.wave_started_ts = current_time

        if self.waiting_wave_gap:
            if current_time >= self.wave_gap_end:
                self.waiting_wave_gap = False
                self.wave_index += 1
                self.spawned_in_wave = 0
                self.current_wave = self._make_wave(self.wave_index)
                self.wave_started_ts = current_time
            else:
                return spawns

        wave = self.current_wave
        if self.spawned_in_wave >= wave["total"]:
            self.waiting_wave_gap = True
            self.wave_gap_end = current_time + wave["wave_gap"]
            return spawns

        if current_time >= self.next_spawn_time:
            batch_size = min(wave["batch"], wave["total"] - self.spawned_in_wave)
            if batch_size > 0:
                count = random.randint(1, batch_size)
                for _ in range(count):
                    e_id = self._pick_enemy_type(wave)
                    row = random.randint(0, 4)
                    spawns.append((e_id, row))
                    self.spawned_in_wave += 1
                self.next_spawn_time = current_time + wave["gap"]

        return spawns

    def _pick_enemy_type(self, wave_def):
        weights = wave_def.get("weights") or {0: 1, 1: 1}
        ids = list(weights.keys())
        probs = list(weights.values())
        return random.choices(ids, weights=probs, k=1)[0]


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
