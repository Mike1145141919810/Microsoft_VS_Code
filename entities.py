import random
import pygame
from constants import (
    SCREEN_WIDTH,
    GRID_START_X,
    GRID_START_Y,
    CELL_WIDTH,
    CELL_HEIGHT,
    GRID_ROWS,
    GRID_COLS,
    PLANT_STATS,
    ENEMY_STATS,
)
from resources import R


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Plant(Sprite):
    def __init__(self, p_id, grid_pos):
        row, col = grid_pos
        x = GRID_START_X + col * CELL_WIDTH - 55
        y = GRID_START_Y + row * CELL_HEIGHT - 55
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
        if self.type == "eco":
            if current_time - self.last_fire > self.fire_rate:
                self.last_fire = current_time
                if game_ref:
                    game_ref.money += 25
            return

        if self.type == "spe" or self.type == "sur":
            return

        lane_enemies = [
            e
            for e in enemies
            if e.row == self.row and e.rect.x > self.rect.x and e.rect.x < SCREEN_WIDTH
        ]
        if not lane_enemies:
            return

        lane_enemies.sort(key=lambda e: e.rect.x)
        target = lane_enemies[0]

        if current_time - self.last_fire > self.fire_rate:
            self.last_fire = current_time
            self.fire(bullets_group, target)

    def fire(self, bullets_group, target=None):
        bx = self.rect.centerx + 20
        by = self.rect.centery - 35
        if self.type == "thr":
            bx -= 20
            by -= 40

        img_key = f"bullet_{self.id+1}"
        b_img = R.get_image(img_key)
        bullet = Bullet(b_img, bx, by, self.damage, self.row, self.type, target)
        bullets_group.add(bullet)


class Bullet(Sprite):
    def __init__(self, image, x, y, damage, row, b_type, target=None):
        super().__init__(image, x, y)
        self.damage = damage
        self.row = row
        self.b_type = b_type
        self.speed = 10
        self.vy = 0
        self.gravity = 0.45
        self.start_y = y

        if b_type == "thr":
            self.speed = 8
            if target:
                tx = target.rect.centerx + random.randint(-20, 20)
                dist = tx - x
                if dist > 0:
                    t = dist / self.speed
                    self.vy = -0.5 * self.gravity * t
            else:
                self.vy = -10

    def update(self):
        if self.b_type == "str":
            self.rect.x += self.speed
        elif self.b_type == "thr":
            self.rect.x += self.speed
            self.rect.y += self.vy
            self.vy += self.gravity
            if self.rect.y > self.start_y + 100:
                self.kill()

        if self.rect.x > SCREEN_WIDTH:
            self.kill()


class Enemy(Sprite):
    def __init__(self, e_id, row):
        self.stats = ENEMY_STATS[e_id]
        img = R.get_image(f"enemy_{e_id+1}")
        center_y = GRID_START_Y + row * CELL_HEIGHT
        x = SCREEN_WIDTH
        y = center_y - 55
        super().__init__(img, x, y)

        self.id = e_id
        self.hp = self.stats["hp"]
        self.speed = self.stats["speed"]
        self.reward = self.stats["reward"]
        self.damage_per_frame = 0.5
        self.row = row
        self.is_attacking = False
        self.target_plant = None
        self.frozen = False

    def update(self, plants_group):
        if self.frozen:
            return

        hit_plants = pygame.sprite.spritecollide(self, plants_group, False)
        target = None
        for p in hit_plants:
            if p.row == self.row:
                if self.rect.right > p.rect.left + 20:
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
