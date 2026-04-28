import random
import math
import pygame

from billo.settings import WIDTH, HEIGHT


class Collectible:
    COLLECT_RADIUS = 20
    GLOW_COLOR     = (255, 255, 255)
    BOB_AMPLITUDE  = 3
    BOB_SPEED      = 0.07
    MARGIN         = 60

    def __init__(self):
        self.x = random.randint(self.MARGIN, WIDTH  - self.MARGIN)
        self.y = random.randint(self.MARGIN, HEIGHT - self.MARGIN)

        self.alive = True
        self.bob_t = random.uniform(0, 2 * math.pi)

    def update(self):
        self.bob_t += self.BOB_SPEED

    def get_draw_pos(self):
        bob_y = int(self.y + math.sin(self.bob_t) * self.BOB_AMPLITUDE)
        return int(self.x), bob_y

    def draw_glow(self, surface, cx, cy):
        glow_r = self.COLLECT_RADIUS + 4

        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha = int(60 + 30 * math.sin(self.bob_t * 2))

        r, g, b = self.GLOW_COLOR
        pygame.draw.circle(glow, (r, g, b, alpha), (glow_r, glow_r), glow_r)

        surface.blit(glow, (cx - glow_r, cy - glow_r))

    def draw(self, surface):
        cx, cy = self.get_draw_pos()
        self.draw_glow(surface, cx, cy)
        self.draw_icon(surface, cx, cy)

    def draw_icon(self, surface, cx, cy):
        raise NotImplementedError

    def apply(self, player):
        raise NotImplementedError
