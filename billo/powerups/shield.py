import random
import math
import pygame

class ShieldPowerUp:
    """Schild-förmiges PowerUp – gewährt einmaligen Schadensschutz."""
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
        bob_y = int(self.y + math.sin(self.bob_t) * 3)
        cx, cy = int(self.x), bob_y

        # Pulsierender Glow
        glow_r = self.COLLECT_RADIUS + 6
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha  = int(50 + 35 * math.sin(self.bob_t * 2))
        pygame.draw.circle(glow_s, (100, 160, 255, alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow_s, (cx - glow_r, cy - glow_r))

        # Schild-Form: klassisches Heroldsschild-Polygon
        #   Breite 24, Höhe 28, spitze Basis
        w, h = 24, 28
        shield_points = [
            (cx - w // 2, cy - h // 2),          # oben links
            (cx + w // 2, cy - h // 2),          # oben rechts
            (cx + w // 2, cy),                   # Mitte rechts
            (cx,           cy + h // 2),         # Spitze unten
            (cx - w // 2, cy),                   # Mitte links
        ]
        # Füllung: blau-silberner Verlauf simuliert durch zwei überlagerte Polygone
        pygame.draw.polygon(surface, (60, 100, 220), shield_points)
        inner = [
            (cx - w // 2 + 4, cy - h // 2 + 4),
            (cx + w // 2 - 4, cy - h // 2 + 4),
            (cx + w // 2 - 4, cy - 2),
            (cx,               cy + h // 2 - 8),
            (cx - w // 2 + 4, cy - 2),
        ]
        pygame.draw.polygon(surface, (140, 180, 255), inner)
        # Rand
        pygame.draw.polygon(surface, WHITE, shield_points, 2)
        # Mittelkreuz als Emblem
        pygame.draw.line(surface, WHITE, (cx, cy - h // 2 + 6), (cx, cy + 2), 2)
        pygame.draw.line(surface, WHITE, (cx - w // 2 + 6, cy - h // 4), (cx + w // 2 - 6, cy - h // 4), 2)


