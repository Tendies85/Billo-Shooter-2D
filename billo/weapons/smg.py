import random
import math
import pygame
from billo.settings import WIDTH, HEIGHT, WHITE


# ── SMG-Geschoss ──────────────────────────────────────────────────────────────
class SMGBullet:
    """Kleineres, schnelleres Projektil der SMG – macht 50 % weniger Schaden."""
    DAMAGE = 12

    def __init__(self, x, y, angle, size_mult=1.0):
        self.x = x
        self.y = y
        self.speed = 13
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.radius = max(1, round(3 * size_mult))
        self.alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if not (0 < self.x < WIDTH and 0 < self.y < HEIGHT):
            self.alive = False

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 160, 30), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x) - 1, int(self.y) - 1), 1)


# ── SMG-Pickup ────────────────────────────────────────────────────────────────
class SMGPickUp:
    """Pickup das die SMG freischaltet. Icon: rotierender Stern."""
    COLLECT_RADIUS = 20

    def __init__(self):
        margin = 60
        self.x     = random.randint(margin, WIDTH  - margin)
        self.y     = random.randint(margin, HEIGHT - margin)
        self.alive = True
        self.bob_t = random.uniform(0, 2 * math.pi)

    def update(self):
        self.bob_t += 0.06

    def draw(self, surface):
        bob_y  = int(self.y + math.sin(self.bob_t) * 3)
        cx, cy = int(self.x), bob_y

        # ── Pulsierender Glow ──
        glow_r = self.COLLECT_RADIUS + 6
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha  = int(50 + 35 * math.sin(self.bob_t * 2))
        pygame.draw.circle(glow_s, (255, 160, 30, alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow_s, (cx - glow_r, cy - glow_r))

        # ── Stern-Icon (5 Zacken, rotierend) ──
        outer_r = 14
        inner_r = 6
        points  = []
        for i in range(10):
            angle = self.bob_t + i * math.pi / 5 - math.pi / 2
            r     = outer_r if i % 2 == 0 else inner_r
            points.append((cx + math.cos(angle) * r,
                           cy + math.sin(angle) * r))

        pygame.draw.polygon(surface, (255, 160, 30), points)
        pygame.draw.polygon(surface, (255, 210, 100), points, 2)
        pygame.draw.circle(surface, WHITE, (cx, cy), 3)
