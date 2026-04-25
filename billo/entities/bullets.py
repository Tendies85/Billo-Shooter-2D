import math
import pygame

from billo.settings import WIDTH, HEIGHT, YELLOW

class Bullet:
    def __init__(self, x, y, angle, size_mult=1.0):
        self.x = x
        self.y = y
        self.speed = 10
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.radius = max(1, round(5 * size_mult))
        self.alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if not (0 < self.x < WIDTH and 0 < self.y < HEIGHT):
            self.alive = False

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)
