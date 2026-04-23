import random
import pygame

class PowerUp:
    """Patronen-förmiges PowerUp – erhöht Schussrate um 2 % pro Einsammlung."""
    COLLECT_RADIUS = 18

    def __init__(self):
        margin = 60
        self.x = random.randint(margin, WIDTH  - margin)
        self.y = random.randint(margin, HEIGHT - margin)
        self.alive    = True
        self.bob_t    = random.uniform(0, 2 * math.pi)  # Schwebeanimation-Phase
        # Goldene Patrone
        self.color_body = (210, 170,  30)   # Messinggelb
        self.color_tip  = (240, 220, 100)   # Helle Spitze
        self.color_rim  = (160, 120,  20)   # Dunkle Hülsenbasis

    def update(self):
        self.bob_t += 0.07   # Schwebetempo

    def draw(self, surface):
        # Patronen-Zeichnung (vertikal, Spitze oben)
        bob_y = int(self.y + math.sin(self.bob_t) * 3)
        cx, cy = int(self.x), bob_y

        # --- Hülse (Rechteck) ---
        hull_w, hull_h = 10, 20
        hull_rect = pygame.Rect(cx - hull_w // 2, cy - hull_h // 2, hull_w, hull_h)
        pygame.draw.rect(surface, self.color_body, hull_rect, border_radius=3)

        # --- Spitze (Dreieck / Polygon oben) ---
        tip_h = 10
        tip_top = cy - hull_h // 2 - tip_h
        tip_points = [
            (cx,              tip_top),
            (cx - hull_w // 2, cy - hull_h // 2),
            (cx + hull_w // 2, cy - hull_h // 2),
        ]
        pygame.draw.polygon(surface, self.color_tip, tip_points)

        # --- Basis-Rand (Primer-Ring) ---
        base_y = cy + hull_h // 2
        pygame.draw.rect(surface, self.color_rim,
                         (cx - hull_w // 2 - 2, base_y - 4, hull_w + 4, 5),
                         border_radius=2)

        # --- Glanzlinie ---
        pygame.draw.line(surface, (255, 240, 160),
                         (cx - 2, cy - hull_h // 2 + 2),
                         (cx - 2, cy + hull_h // 2 - 4), 2)

        # --- Leuchtender Ring drum herum ---
        glow_r = self.COLLECT_RADIUS
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha = int(60 + 30 * math.sin(self.bob_t * 2))
        pygame.draw.circle(glow_surf, (255, 220, 50, alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow_surf, (cx - glow_r, bob_y - glow_r))
