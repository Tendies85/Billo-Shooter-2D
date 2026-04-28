import math
import pygame

from billo.collectibles import Collectible
from billo.settings import WHITE


class Trinket(Collectible):
    COLLECT_RADIUS = 22
    GLOW_COLOR     = (180, 80, 255)

    def __init__(self):
        super().__init__()
        self._rot = 0.0

    def update(self):
        super().update()
        self._rot += 2.0

    def draw(self, surface):
        cx, cy = self.get_draw_pos()

        # stronger glow
        self.draw_glow(surface, cx, cy)

        # background disk
        pygame.draw.circle(surface, (60, 20, 90), (cx, cy), self.COLLECT_RADIUS)
        pygame.draw.circle(surface, self.GLOW_COLOR, (cx, cy), self.COLLECT_RADIUS, 2)

        # icon
        self.draw_icon(surface, cx, cy)

        # rotating sparkle
        angle = math.radians(self._rot)
        sx = int(cx + math.cos(angle) * (self.COLLECT_RADIUS - 2))
        sy = int(cy + math.sin(angle) * (self.COLLECT_RADIUS - 2))
        pygame.draw.circle(surface, WHITE, (sx, sy), 2)



class SwiftnessTrinket(Trinket):
    GLOW_COLOR = (255, 220, 40)

    def draw_icon(self, surface, cx, cy):
        bolt = [
            (cx + 4,  cy - 14),
            (cx - 2,  cy - 2),
            (cx + 4,  cy - 2),
            (cx - 4,  cy + 14),
            (cx + 2,  cy + 2),
            (cx - 4,  cy + 2),
        ]
        pygame.draw.polygon(surface, (255, 230, 50), bolt)
        pygame.draw.polygon(surface, WHITE, bolt, 1)

    def on_collect(self, player):
        if not getattr(player, "has_swiftness", False):
            player.has_swiftness = True
            player.speed *= 1.15



FPS             = 60
ORBIT_RADIUS    = 55      # Pixel Abstand vom Spieler
ORBIT_SPEED     = 1.8     # Grad pro Frame
SHOOT_INTERVAL  = 2 * FPS  # alle 2 Sekunden


class OrbitalBullet:
    """Kleines Projektil das der Satellit abfeuert."""
    DAMAGE = 20

    def __init__(self, x, y, angle):
        self.x     = x
        self.y     = y
        speed      = 9
        self.dx    = math.cos(angle) * speed
        self.dy    = math.sin(angle) * speed
        self.radius = 4
        self.alive  = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if not (0 < self.x < WIDTH and 0 < self.y < HEIGHT):
            self.alive = False

    def draw(self, surface):
        pygame.draw.circle(surface, (180, 100, 255), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE,            (int(self.x), int(self.y)), self.radius, 1)


class OrbitalSatellite:
    """
    Kleine unzerstörbare Kugel die um den Spieler kreist und alle 2s schießt.
    Wird vom Spieler-State gehalten, vom Renderer gezeichnet, vom Game geupdated.
    """

    def __init__(self, offset_angle=0.0):
        self.angle        = offset_angle   # aktuelle Orbitposition (Rad)
        self.shoot_timer  = random.randint(0, SHOOT_INTERVAL)   # versetzt starten
        self.bullets      = []
        self._pulse       = random.uniform(0, math.pi * 2)

    # Position berechnen
    def get_pos(self, px, py):
        x = px + math.cos(self.angle) * ORBIT_RADIUS
        y = py + math.sin(self.angle) * ORBIT_RADIUS
        return x, y

    def update(self, px, py, enemies):
        """enemies: Liste aller lebenden Gegner (Zombie / Clonker)."""
        # Orbit
        self.angle     = (self.angle + math.radians(ORBIT_SPEED)) % (2 * math.pi)
        self._pulse   += 0.1

        # Schuss-Timer
        self.shoot_timer += 1
        if self.shoot_timer >= SHOOT_INTERVAL:
            self.shoot_timer = 0
            self._fire(px, py, enemies)

        # Eigene Bullets updaten
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.alive]

    def _fire(self, px, py, enemies):
        """Schießt auf den nächsten Gegner."""
        sx, sy = self.get_pos(px, py)
        if not enemies:
            return
        # Nächsten Gegner finden
        nearest = min(enemies, key=lambda e: math.hypot(e.x - sx, e.y - sy))
        angle   = math.atan2(nearest.y - sy, nearest.x - sx)
        self.bullets.append(OrbitalBullet(sx, sy, angle))

    def draw(self, surface, px, py):
        sx, sy = self.get_pos(px, py)
        cx, cy = int(sx), int(sy)

        # Orbit-Linie (gestrichelt / halbtransparent)
        orbit_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(orbit_surf, (180, 100, 255, 30),
                           (int(px), int(py)), ORBIT_RADIUS, 1)
        surface.blit(orbit_surf, (0, 0))

        # Glow
        pulse_alpha = int(80 + 50 * math.sin(self._pulse))
        glow_r = 14
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (180, 100, 255, pulse_alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow_s, (cx - glow_r, cy - glow_r))

        # Kugel-Körper
        pygame.draw.circle(surface, (130, 60, 200), (cx, cy), 8)
        pygame.draw.circle(surface, (200, 140, 255), (cx, cy), 8, 2)
        # Glanzpunkt
        pygame.draw.circle(surface, WHITE, (cx - 2, cy - 2), 2)

        # Eigene Bullets zeichnen
        for b in self.bullets:
            b.draw(surface)


class OrbitalMiniME(Trinket):
    GLOW_COLOR = (160, 80, 255)

    def draw_icon(self, surface, cx, cy):
        pygame.draw.circle(surface, (200, 150, 255), (cx, cy), 6)
        pygame.draw.circle(surface, (180, 100, 255), (cx, cy), 14, 1)
        pygame.draw.circle(surface, WHITE, (cx + 14, cy), 3)

    def on_collect(self, player):
        if not hasattr(player, "satellites"):
            player.satellites = []

        offset = len(player.satellites) * (
            2 * math.pi / max(1, len(player.satellites) + 1)
        )

        player.satellites.append(
            OrbitalSatellite(offset_angle=offset)
        )


