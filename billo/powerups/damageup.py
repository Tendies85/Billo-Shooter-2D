import random
import math
import pygame

from billo.settings import WIDTH, HEIGHT, WHITE


class DamageUp:
    """
    PowerUp – erhöht Waffenschaden um 2 % pro Einsammlung. Stapelbar.
    Icon: Patrone mit Pfeil nach oben (rot/orange).
    """
    COLLECT_RADIUS = 18

    def __init__(self):
        margin = 60
        self.x     = random.randint(margin, WIDTH  - margin)
        self.y     = random.randint(margin, HEIGHT - margin)
        self.alive = True
        self.bob_t = random.uniform(0, 2 * math.pi)

        # Rote Patrone
        self.color_body = (180,  40,  40)   # Dunkelrot
        self.color_tip  = (230,  80,  80)   # Hellrot Spitze
        self.color_rim  = (120,  20,  20)   # Dunkler Rand
        self.color_arrow = (255, 200,  50)  # Goldgelber Pfeil

    def update(self):
        self.bob_t += 0.07

    def draw(self, surface):
        bob_y  = int(self.y + math.sin(self.bob_t) * 3)
        cx, cy = int(self.x), bob_y

        # --- Leuchtender Glow ---
        glow_r    = self.COLLECT_RADIUS
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha     = int(60 + 30 * math.sin(self.bob_t * 2))
        pygame.draw.circle(glow_surf, (255, 80, 80, alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow_surf, (cx - glow_r, bob_y - glow_r))

        # --- Hülse ---
        hull_w, hull_h = 10, 20
        hull_rect = pygame.Rect(cx - hull_w // 2, cy - hull_h // 2, hull_w, hull_h)
        pygame.draw.rect(surface, self.color_body, hull_rect, border_radius=3)

        # --- Spitze ---
        tip_h  = 10
        tip_top = cy - hull_h // 2 - tip_h
        tip_points = [
            (cx,               tip_top),
            (cx - hull_w // 2, cy - hull_h // 2),
            (cx + hull_w // 2, cy - hull_h // 2),
        ]
        pygame.draw.polygon(surface, self.color_tip, tip_points)

        # --- Basis-Rand ---
        base_y = cy + hull_h // 2
        pygame.draw.rect(surface, self.color_rim,
                         (cx - hull_w // 2 - 2, base_y - 4, hull_w + 4, 5),
                         border_radius=2)

        # --- Glanzlinie ---
        pygame.draw.line(surface, (255, 140, 140),
                         (cx - 2, cy - hull_h // 2 + 2),
                         (cx - 2, cy + hull_h // 2 - 4), 2)

        # --- Pfeil nach oben (auf der Hülse) ---
        # Schaft
        arrow_x  = cx + 3
        arrow_top = cy - 6
        arrow_bot = cy + 7
        pygame.draw.line(surface, self.color_arrow,
                         (arrow_x, arrow_bot), (arrow_x, arrow_top), 2)
        # Pfeilspitze (kleines Dreieck)
        head = [
            (arrow_x,     arrow_top - 1),
            (arrow_x - 3, arrow_top + 4),
            (arrow_x + 3, arrow_top + 4),
        ]
        pygame.draw.polygon(surface, self.color_arrow, head)
