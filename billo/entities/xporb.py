import random
import math
import pygame

from billo.settings import WIDTH, HEIGHT


class XPOrb:
    """
    Kleiner Erfahrungspunkt-Orb der beim Tod eines Zombies erscheint.
    Wert: 1 XP. Wird vom Spieler durch Berührung eingesammelt.
    Bewegt sich langsam auf den Spieler zu sobald er nah genug ist.
    """
    VALUE          = 1
    COLLECT_RADIUS = 12
    ATTRACT_RANGE  = 120   # Pixel – ab dieser Distanz zieht der Orb zum Spieler
    ATTRACT_SPEED  = 4.0

    # Farben
    _INNER = (120, 255, 180)   # helles Mintgrün
    _OUTER = ( 40, 180, 100)   # dunkleres Grün
    _GLOW  = ( 60, 220, 120)

    def __init__(self, x, y):
        # Leichter Streuversatz damit Orbs nicht alle übereinander liegen
        self.x     = x + random.uniform(-12, 12)
        self.y     = y + random.uniform(-12, 12)
        self.alive = True
        self.bob_t = random.uniform(0, 2 * math.pi)
        # Kurzer initialer Impuls (auseinanderdriften)
        angle  = random.uniform(0, 2 * math.pi)
        speed  = random.uniform(1.0, 2.5)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.friction = 0.88   # Abbremsen nach initialem Impuls

    def update(self, px, py):
        self.bob_t += 0.12

        dist = math.hypot(px - self.x, py - self.y)

        if dist < self.ATTRACT_RANGE and dist > 0:
            # Zum Spieler hingezogen
            self.dx = (px - self.x) / dist * self.ATTRACT_SPEED
            self.dy = (py - self.y) / dist * self.ATTRACT_SPEED
        else:
            # Initialer Impuls bremst ab
            self.dx *= self.friction
            self.dy *= self.friction

        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.bob_t) * 2)

        # Äußerer Glow
        glow_r = 10
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha  = int(60 + 40 * math.sin(self.bob_t))
        pygame.draw.circle(glow_s, (*self._GLOW, alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow_s, (cx - glow_r, cy - glow_r))

        # Orb-Körper
        pygame.draw.circle(surface, self._OUTER, (cx, cy), 5)
        pygame.draw.circle(surface, self._INNER, (cx, cy), 3)
        # Glanzpunkt
        pygame.draw.circle(surface, (200, 255, 220), (cx - 1, cy - 1), 1)
