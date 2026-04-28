import math
import pygame
from billo.collectible import Collectible
from billo.settings import WHITE


class LaserPickup(Collectible):
    COLLECT_RADIUS = 20
    GLOW_COLOR     = (255, 80, 80)

    def __init__(self):
        super().__init__()
        self.rot = 0.0

    def update(self):
        super().update()
        self.rot += 1.5

    def draw_icon(self, surface, cx, cy):
        rot_r = math.radians(self.rot)

        for i in range(4):
            angle = rot_r + i * math.pi / 2
            ax = cx + math.cos(angle) * 14
            ay = cy + math.sin(angle) * 14
            pygame.draw.line(surface, (255, 60, 60),
                             (cx, cy), (int(ax), int(ay)), 5)

        pygame.draw.circle(surface, (255, 120, 120), (cx, cy), 6)
        pygame.draw.circle(surface, WHITE, (cx, cy), 6, 2)

    def on_collect(self, player):
        player.has_laser = True


class ShotgunPickup(Collectible):
    COLLECT_RADIUS = 20
    GLOW_COLOR     = (255, 120, 30)

    def draw_icon(self, surface, cx, cy):
        # barrel
        pygame.draw.rect(surface, (180, 130, 60),
                         (cx - 9, cy - 3, 18, 7),
                         border_radius=2)
        pygame.draw.rect(surface, WHITE,
                         (cx - 9, cy - 3, 18, 7), 1,
                         border_radius=2)

        # spread dots
        for deg in [-25, 0, 25]:
            rad = math.radians(-90 + deg)
            bx  = int(cx + math.cos(rad) * 16)
            by  = int(cy + math.sin(rad) * 16)

            pygame.draw.circle(surface, (255, 160, 50), (bx, by), 3)
            pygame.draw.circle(surface, WHITE, (bx, by), 3, 1)

            pygame.draw.line(surface, (200, 140, 60),
                             (cx, cy - 3), (bx, by), 1)

    def on_collect(self, player):
        player.has_shotgun = True


class SMGPickup(Collectible):
    COLLECT_RADIUS = 20
    GLOW_COLOR     = (255, 160, 30)

    def draw_icon(self, surface, cx, cy):
        outer_r = 14
        inner_r = 6
        points  = []

        for i in range(10):
            angle = self.bob_t + i * math.pi / 5 - math.pi / 2
            r     = outer_r if i % 2 == 0 else inner_r
            points.append((cx + math.cos(angle) * r,
                           cy + math.sin(angle) * r))

        pygame.draw.polygon(surface, (255, 160, 30), points)
        pygame.draw.polygon(surface, (255, 210, 100), points, 2)
        pygame.draw.circle(surface, WHITE, (cx, cy), 3)

    def on_collect(self, player):
        player.has_smg = True

