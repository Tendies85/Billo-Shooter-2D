import random
import math
import pygame
from billo.settings import WIDTH, HEIGHT, WHITE


class Laser:
    """Dauerhafter Laserstrahl vom Spieler zur Maus – verursacht alle 30 Frames Schaden."""
    DAMAGE      = 18
    TICK_FRAMES = 30   # alle 0.5 s

    def __init__(self, px, py, angle):
        self.px    = px
        self.py    = py
        self.angle = angle
        far = max(WIDTH, HEIGHT) * 2
        self.ex = px + math.cos(angle) * far
        self.ey = py + math.sin(angle) * far
        self.flicker = random.randint(0, 3)

    def draw(self, surface, frame):
        flicker_w = 3 + (frame + self.flicker) % 2
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(glow, (255, 60, 60, 60),
                         (int(self.px), int(self.py)),
                         (int(self.ex), int(self.ey)), flicker_w + 6)
        surface.blit(glow, (0, 0))
        pygame.draw.line(surface, (255, 255, 255),
                         (int(self.px), int(self.py)),
                         (int(self.ex), int(self.ey)), flicker_w)
        pygame.draw.line(surface, (255, 80, 80),
                         (int(self.px), int(self.py)),
                         (int(self.ex), int(self.ey)), max(1, flicker_w - 2))

    @staticmethod
    def ray_hits_circle(px, py, angle, cx, cy, radius):
        dx = math.cos(angle)
        dy = math.sin(angle)
        fx = cx - px
        fy = cy - py
        t = fx * dx + fy * dy
        if t < 0:
            return False
        nx = px + dx * t
        ny = py + dy * t
        return math.hypot(cx - nx, cy - ny) <= radius


class LaserWeaponPickUp:
    """
    Pickup das die Laserwaffe freischaltet.
    Früher: LaserPowerUp  →  jetzt unter billo.weapons
    """
    COLLECT_RADIUS = 20

    def __init__(self):
        margin = 60
        self.x     = random.randint(margin, WIDTH  - margin)
        self.y     = random.randint(margin, HEIGHT - margin)
        self.alive = True
        self.bob_t = random.uniform(0, 2 * math.pi)
        self.rot   = 0.0

    def update(self):
        self.bob_t += 0.06
        self.rot   += 1.5

    def draw(self, surface):
        bob_y  = int(self.y + math.sin(self.bob_t) * 3)
        cx, cy = int(self.x), bob_y
        rot_r  = math.radians(self.rot)

        glow_r = self.COLLECT_RADIUS + 6
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha  = int(50 + 35 * math.sin(self.bob_t * 2))
        pygame.draw.circle(glow_s, (255, 80, 80, alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow_s, (cx - glow_r, cy - glow_r))

        arm_len = 14
        arm_w   = 5
        for i in range(4):
            angle = rot_r + i * math.pi / 2
            ax = cx + math.cos(angle) * arm_len
            ay = cy + math.sin(angle) * arm_len
            pygame.draw.line(surface, (255, 60, 60), (cx, cy), (int(ax), int(ay)), arm_w)

        pygame.draw.circle(surface, (255, 120, 120), (cx, cy), 6)
        pygame.draw.circle(surface, WHITE, (cx, cy), 6, 2)
