import math
import pygame

from billo.settings import WHITE
from billo.trinkets.base import BaseTrinket


class SwiftnessTrinket(BaseTrinket):
    """
    Trinket – Swiftness
    Verleiht dem Spieler dauerhaft +15 % Bewegungsgeschwindigkeit.
    Nicht stapelbar.
    Icon: stilisierter Blitz.
    """
    GLOW_COLOR = (255, 220, 40)   # Gold
    LABEL      = "Swiftness"

    def draw_icon(self, surface, cx, cy):
        # Blitz-Polygon (klassische Zickzack-Form)
        bolt = [
            (cx + 4,  cy - 14),   # Spitze oben-rechts
            (cx - 2,  cy - 2),    # Mitte links
            (cx + 4,  cy - 2),    # Mitte rechts (Knick)
            (cx - 4,  cy + 14),   # Spitze unten-links
            (cx + 2,  cy + 2),    # Mitte rechts unten
            (cx - 4,  cy + 2),    # Mitte links unten (Knick)
        ]
        pygame.draw.polygon(surface, (255, 230, 50), bolt)
        pygame.draw.polygon(surface, WHITE, bolt, 1)

    def apply(self, player):
        if not getattr(player, "has_swiftness", False):
            player.has_swiftness = True
            player.speed *= 1.15
