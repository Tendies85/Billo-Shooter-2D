import random
import math
import pygame

from billo.settings import WIDTH, HEIGHT, RED, GREEN

# Basis-Zombie-Werte (müssen mit zombies.py übereinstimmen)
ZOMBIE_RADIUS = 14
ZOMBIE_HP_BASE = 30   # 30 + wave * 5
ZOMBIE_SPEED_BASE = 1.2


class Clonker:
    """
    Starker Gegner.
    - 50 % größer als Zombie (radius = 21)
    - 25 % langsamer
    - 200 % HP (Zombie-HP × 2)
    - Kleines Horn auf dem Kopf
    """

    def __init__(self, wave):
        # Spawn am Rand
        side = random.randint(0, 3)
        if side == 0: self.x, self.y = random.randint(0, WIDTH), -30
        elif side == 1: self.x, self.y = WIDTH + 30, random.randint(0, HEIGHT)
        elif side == 2: self.x, self.y = random.randint(0, WIDTH), HEIGHT + 30
        else:           self.x, self.y = -30, random.randint(0, HEIGHT)

        self.radius = int(ZOMBIE_RADIUS * 1.5)               # 21
        base_hp     = (ZOMBIE_HP_BASE + wave * 5) * 2        # 200% HP
        self.hp     = base_hp
        self.max_hp = base_hp
        self.speed  = (ZOMBIE_SPEED_BASE + wave * 0.1 + random.uniform(0, 0.3)) * 0.75  # 25% langsamer
        self.alive  = True

        # Dunkles Graugrün – unterscheidet sich vom Zombie
        g = random.randint(55, 90)
        self.color       = (55, g, 55)
        self.color_dark  = (30, max(30, g - 30), 30)

    def update(self, px, py):
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        r = self.radius

        # ── Körper ──
        pygame.draw.circle(surface, self.color,      (cx, cy), r)
        pygame.draw.circle(surface, self.color_dark, (cx, cy), r, 3)

        # ── Horn auf dem Kopf ──
        # Winkel: gerade nach oben (270°)
        horn_base_y = cy - r + 2
        horn_points = [
            (cx - 5, horn_base_y),          # Basis links
            (cx + 5, horn_base_y),          # Basis rechts
            (cx,     horn_base_y - 14),     # Spitze
        ]
        pygame.draw.polygon(surface, (180, 140, 40), horn_points)   # goldbraunes Horn
        pygame.draw.polygon(surface, (220, 180, 60), horn_points, 1)

        # ── Augen (größer als beim Zombie) ──
        eye_y = cy - 5
        pygame.draw.circle(surface, RED, (cx + 7,  eye_y), 4)
        pygame.draw.circle(surface, RED, (cx - 7,  eye_y), 4)
        # Pupillen
        pygame.draw.circle(surface, (60, 0, 0), (cx + 7,  eye_y), 2)
        pygame.draw.circle(surface, (60, 0, 0), (cx - 7,  eye_y), 2)

        # ── Mini-HP-Bar (breiter) ──
        bar_w = int(r * 2.2)
        bx    = cx - bar_w // 2
        by    = cy - r - 10
        pygame.draw.rect(surface, RED,   (bx, by, bar_w, 5))
        pygame.draw.rect(surface, GREEN, (bx, by, int(bar_w * self.hp / self.max_hp), 5))
        pygame.draw.rect(surface, (80, 80, 80), (bx, by, bar_w, 5), 1)

    def hit(self, damage=25):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True
        return False
