import random
import math
import pygame

from billo.settings import WIDTH, HEIGHT, RED, GREEN, BLUE

class Zombie:
    def __init__(self, wave):
        # Spawn am Rand
        side = random.randint(0, 3)
        if side == 0: self.x, self.y = random.randint(0, WIDTH), -20
        elif side == 1: self.x, self.y = WIDTH + 20, random.randint(0, HEIGHT)
        elif side == 2: self.x, self.y = random.randint(0, WIDTH), HEIGHT + 20
        else:           self.x, self.y = -20, random.randint(0, HEIGHT)

        self.radius = 14
        self.hp     = 30 + wave * 5
        self.max_hp = self.hp
        self.speed  = 1.2 + wave * 0.1 + random.uniform(0, 0.4)
        self.alive  = True
        # Zufällige Grün-/Grauton-Farbe
        g = random.randint(80, 130)
        self.color = (40, g, 40)

    def update(self, px, py):
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self, surface):
        # Körper
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (200, 50, 50), (int(self.x), int(self.y)), self.radius, 2)
        # Augen
        ex = int(self.x + 5)
        ey = int(self.y - 4)
        pygame.draw.circle(surface, RED, (ex, ey), 3)
        pygame.draw.circle(surface, RED, (ex - 10, ey), 3)
        # Mini-HP-Bar
        bar_w = 28
        bx = int(self.x) - bar_w // 2
        by = int(self.y) - self.radius - 8
        pygame.draw.rect(surface, RED,   (bx, by, bar_w, 4))
        pygame.draw.rect(surface, GREEN, (bx, by, int(bar_w * self.hp / self.max_hp), 4))

    def hit(self, damage=25):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True
        return False
