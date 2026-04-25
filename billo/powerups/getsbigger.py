import random
import math
import pygame

from billo.settings import WIDTH, HEIGHT, WHITE


class GetsBigger:
    """
    PowerUp – vergrößert Projektile und Laserstrahl um 3% pro Stack. Stapelbar.
    Icon: breiter Pfeil nach oben (grün/türkis).
    """
    COLLECT_RADIUS = 18

    def __init__(self):
        margin = 60
        self.x     = random.randint(margin, WIDTH  - margin)
        self.y     = random.randint(margin, HEIGHT - margin)
        self.alive = True
        self.bob_t = random.uniform(0, 2 * math.pi)

    def update(self):
        self.bob_t += 0.07

    def draw(self, surface):
        bob_y  = int(self.y + math.sin(self.bob_t) * 3)
        cx, cy = int(self.x), bob_y

        # --- Leuchtender Glow (türkis) ---
        glow_r    = self.COLLECT_RADIUS
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha     = int(60 + 30 * math.sin(self.bob_t * 2))
        pygame.draw.circle(glow_surf, (50, 220, 180, alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow_surf, (cx - glow_r, bob_y - glow_r))

        # --- Breiter Pfeil nach oben ---
        # Pfeilkopf (großes breites Dreieck)
        head_w  = 22
        head_h  = 14
        head_top = cy - 10
        head = [
            (cx,            head_top),           # Spitze
            (cx - head_w,   head_top + head_h),  # links
            (cx + head_w,   head_top + head_h),  # rechts
        ]
        pygame.draw.polygon(surface, (50, 220, 160), head)
        pygame.draw.polygon(surface, WHITE, head, 1)

        # Schaft (breites Rechteck)
        shaft_w = 10
        shaft_top = head_top + head_h
        shaft_bot = cy + 14
        shaft = pygame.Rect(cx - shaft_w, shaft_top, shaft_w * 2, shaft_bot - shaft_top)
        pygame.draw.rect(surface, (40, 190, 140), shaft)
        pygame.draw.rect(surface, WHITE, shaft, 1)
