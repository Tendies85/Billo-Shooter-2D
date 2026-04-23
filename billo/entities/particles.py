import random
import pygame
import math

class Particle:
    """Kleines Blut-/Treffer-Partikel."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle  = random.uniform(0, 2 * math.pi)
        speed  = random.uniform(1, 4)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.life = random.randint(15, 30)
        self.color = color

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, self.life * 8)
        r = max(2, self.life // 6)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)
