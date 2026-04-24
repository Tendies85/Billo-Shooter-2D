import random
import math
import pygame

from billo.settings import WIDTH, HEIGHT, WHITE


class BaseTrinket:
    """
    Abstrakte Basisklasse für alle Trinkets.

    Trinkets sind seltene (3 % pro Welle) sammelbare Items die dem Spieler
    besondere passive Fähigkeiten verleihen.

    Unterklassen müssen implementieren:
        - draw_icon(surface, cx, cy)  – das spezifische Icon zeichnen
        - apply(player)               – den Effekt auf den Spieler anwenden

    Optionale Klassenvariablen zum Überschreiben:
        COLLECT_RADIUS  (default 22)
        GLOW_COLOR      (default lila)
        LABEL           (default Klassenname)
    """
    COLLECT_RADIUS = 22
    GLOW_COLOR     = (180, 80, 255)   # Lila – erkennbar als Trinket
    LABEL          = "Trinket"

    def __init__(self):
        margin    = 80
        self.x    = random.randint(margin, WIDTH  - margin)
        self.y    = random.randint(margin, HEIGHT - margin)
        self.alive = True
        self.bob_t = random.uniform(0, 2 * math.pi)
        self._rot  = 0.0   # rotierender Glanzpunkt

    def update(self):
        self.bob_t += 0.05
        self._rot  += 2.0

    def draw(self, surface):
        bob_y  = int(self.y + math.sin(self.bob_t) * 4)
        cx, cy = int(self.x), bob_y

        # ── Äußerer Glow (lila, pulsierend) ──
        glow_r = self.COLLECT_RADIUS + 10
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha  = int(55 + 45 * math.sin(self.bob_t * 1.8))
        r, g, b = self.GLOW_COLOR
        pygame.draw.circle(glow_s, (r, g, b, alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow_s, (cx - glow_r, cy - glow_r))

        # ── Hintergrundkreis (dunkles Lila) ──
        pygame.draw.circle(surface, (60, 20, 90), (cx, cy), self.COLLECT_RADIUS)
        pygame.draw.circle(surface, self.GLOW_COLOR, (cx, cy), self.COLLECT_RADIUS, 2)

        # ── Konkretes Icon (Unterklasse) ──
        self.draw_icon(surface, cx, cy)

        # ── Rotierender Glanzpunkt am Rand ──
        gp_angle = math.radians(self._rot)
        gpx = int(cx + math.cos(gp_angle) * (self.COLLECT_RADIUS - 2))
        gpy = int(cy + math.sin(gp_angle) * (self.COLLECT_RADIUS - 2))
        pygame.draw.circle(surface, WHITE, (gpx, gpy), 2)

    def draw_icon(self, surface, cx, cy):
        """Muss von jeder Unterklasse überschrieben werden."""
        raise NotImplementedError

    def apply(self, player):
        """Wendet den Trinket-Effekt auf den Spieler an. Muss überschrieben werden."""
        raise NotImplementedError
