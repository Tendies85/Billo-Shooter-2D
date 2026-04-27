import random
import math
import pygame
from billo.settings import WIDTH, HEIGHT, WHITE


# ── Shotgun-Projektil ────────────────────────────────────────────────────────
class ShotgunBullet:
    """
    Einzelnes Shotgun-Pellet.
    Maximale Reichweite: 20% des Bildschirms (gemessen an WIDTH).
    Schaden: 15 pro Pellet (3 Pellets = 45 gesamt).
    """
    DAMAGE       = 15
    MAX_DISTANCE = WIDTH * 0.20   # 20% der Bildschirmbreite

    def __init__(self, x, y, angle, size_mult=1.0):
        self.x           = x
        self.y           = y
        self.start_x     = x
        self.start_y     = y
        self.speed       = 12
        self.dx          = math.cos(angle) * self.speed
        self.dy          = math.sin(angle) * self.speed
        self.radius      = max(1, round(4 * size_mult))
        self.alive       = True

    def update(self):
        self.x += self.dx
        self.y += self.dy

        # Reichweite prüfen
        dist = math.hypot(self.x - self.start_x, self.y - self.start_y)
        if dist >= self.MAX_DISTANCE:
            self.alive = False
            return

        if not (0 < self.x < WIDTH and 0 < self.y < HEIGHT):
            self.alive = False

    def draw(self, surface):
        # Orange-rotes Pellet mit hellem Kern
        pygame.draw.circle(surface, (255, 120, 30), (int(self.x), int(self.y)), self.radius)
        if self.radius > 2:
            pygame.draw.circle(surface, (255, 220, 120), (int(self.x), int(self.y)), max(1, self.radius - 2))


# ── Shotgun-Pickup ────────────────────────────────────────────────────────────
class ShotgunPickUp:
    """
    Pickup das die Shotgun freischaltet.
    Icon: drei Punkte in Fächerform (symbolisiert Streuung).
    """
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

        # ── Pulsierender Glow (orange) ──
        glow_r = self.COLLECT_RADIUS + 6
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha  = int(50 + 35 * math.sin(self.bob_t * 2))
        pygame.draw.circle(glow_s, (255, 120, 30, alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow_s, (cx - glow_r, cy - glow_r))

        # ── Lauf (kurzes breites Rechteck) ──
        barrel_w, barrel_h = 18, 7
        pygame.draw.rect(surface, (180, 130, 60),
                         (cx - barrel_w // 2, cy - barrel_h // 2, barrel_w, barrel_h),
                         border_radius=2)
        pygame.draw.rect(surface, WHITE,
                         (cx - barrel_w // 2, cy - barrel_h // 2, barrel_w, barrel_h),
                         1, border_radius=2)

        # ── Drei Streupunkte (Fächer nach oben) ──
        spread_angles = [-25, 0, 25]   # Grad relativ nach oben
        for deg in spread_angles:
            rad   = math.radians(-90 + deg)
            dist  = 16
            bx    = int(cx + math.cos(rad) * dist)
            by_   = int(cy + math.sin(rad) * dist)
            pygame.draw.circle(surface, (255, 160, 50), (bx, by_), 3)
            pygame.draw.circle(surface, WHITE,          (bx, by_), 3, 1)

        # ── Drei Strahlen vom Lauf zu den Punkten ──
        for deg in spread_angles:
            rad  = math.radians(-90 + deg)
            dist = 16
            bx   = int(cx + math.cos(rad) * dist)
            by_  = int(cy + math.sin(rad) * dist)
            pygame.draw.line(surface, (200, 140, 60, 180),
                             (cx, cy - barrel_h // 2), (bx, by_), 1)
