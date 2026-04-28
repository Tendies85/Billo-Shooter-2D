import random
import math
import pygame

from billo.collectibles.physics import PhysicsCollectible


class XPOrb(PhysicsCollectible):
    VALUE          = 1
    COLLECT_RADIUS = 12

    ATTRACT_RANGE  = 120
    ATTRACT_SPEED  = 4.0

    GLOW_COLOR     = (60, 220, 120)

    _INNER = (120, 255, 180)
    _OUTER = (40, 180, 100)

    def __init__(self, x, y):
        super().__init__(x, y)

        # small spawn scatter
        self.x += random.uniform(-12, 12)
        self.y += random.uniform(-12, 12)

        # initial burst
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.0, 2.5)

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.friction = 0.88

    def update(self, player):
        super().update()

        px, py = player.x, player.y

        attracted = self.attract_to(
            px, py,
            self.ATTRACT_SPEED,
            self.ATTRACT_RANGE
        )

        if not attracted:
            self.apply_friction()

        self.apply_velocity()

    def draw(self, surface):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.bob_t) * 2)

        glow_r = 10
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha = int(60 + 40 * math.sin(self.bob_t))

        pygame.draw.circle(glow, (*self.GLOW_COLOR, alpha),
                           (glow_r, glow_r), glow_r)

        surface.blit(glow, (cx - glow_r, cy - glow_r))

        self.draw_icon(surface, cx, cy)

    def draw_icon(self, surface, cx, cy):
        pygame.draw.circle(surface, self._OUTER, (cx, cy), 5)
        pygame.draw.circle(surface, self._INNER, (cx, cy), 3)
        pygame.draw.circle(surface, (200, 255, 220), (cx - 1, cy - 1), 1)

    def on_collect(self, player):
        player.xp += self.VALUE
