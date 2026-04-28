import math
import pygame

from billo.settings import WHITE
from billo.collectibles import Collectible

class PowerUp(Collectible):
    pass


class DamageUp(PowerUp):
    GLOW_COLOR = (255, 80, 80)

    def draw_icon(self, surface, cx, cy):
        hull_w, hull_h = 10, 20
        pygame.draw.rect(surface, (180, 40, 40),
                         (cx - hull_w // 2, cy - hull_h // 2, hull_w, hull_h),
                         border_radius=3)
        pygame.draw.polygon(surface, (230, 80, 80), [
            (cx, cy - hull_h // 2 - 10),
            (cx - hull_w // 2, cy - hull_h // 2),
            (cx + hull_w // 2, cy - hull_h // 2),
        ])
        pygame.draw.line(surface, (255, 200, 50),
                         (cx + 3, cy + 7), (cx + 3, cy - 6), 2)

    def apply(self, player):
        player.damage *= 1.02


class GetsBigger(PowerUp):
    GLOW_COLOR = (50, 220, 180)

    def draw_icon(self, surface, cx, cy):
        head_w, head_h = 22, 14
        head_top = cy - 10

        # head
        head = [
            (cx, head_top),
            (cx - head_w, head_top + head_h),
            (cx + head_w, head_top + head_h),
        ]
        pygame.draw.polygon(surface, (50, 220, 160), head)
        pygame.draw.polygon(surface, WHITE, head, 1)

        # shaft
        shaft = pygame.Rect(cx - 10, head_top + head_h, 20, 24)
        pygame.draw.rect(surface, (40, 190, 140), shaft)
        pygame.draw.rect(surface, WHITE, shaft, 1)

    def apply(self, player):
        player.projectile_scale *= 1.03




class BulletTime(PowerUp):
    GLOW_COLOR = (255, 220, 50)

    def draw_icon(self, surface, cx, cy):
        hull_w, hull_h = 10, 20

        pygame.draw.rect(surface, (210, 170, 30),
                         (cx - hull_w // 2, cy - hull_h // 2, hull_w, hull_h),
                         border_radius=3)

        pygame.draw.polygon(surface, (240, 220, 100), [
            (cx, cy - hull_h // 2 - 10),
            (cx - hull_w // 2, cy - hull_h // 2),
            (cx + hull_w // 2, cy - hull_h // 2),
        ])

        pygame.draw.rect(surface, (160, 120, 20),
                         (cx - hull_w // 2 - 2, cy + hull_h // 2 - 4, hull_w + 4, 5),
                         border_radius=2)

    def apply(self, player):
        player.fire_rate *= 1.02


class ShieldPowerUp(PowerUp):
    COLLECT_RADIUS = 20
    GLOW_COLOR     = (100, 160, 255)

    def draw_icon(self, surface, cx, cy):
        w, h = 24, 28

        outer = [
            (cx - w // 2, cy - h // 2),
            (cx + w // 2, cy - h // 2),
            (cx + w // 2, cy),
            (cx, cy + h // 2),
            (cx - w // 2, cy),
        ]

        inner = [
            (cx - w // 2 + 4, cy - h // 2 + 4),
            (cx + w // 2 - 4, cy - h // 2 + 4),
            (cx + w // 2 - 4, cy - 2),
            (cx, cy + h // 2 - 8),
            (cx - w // 2 + 4, cy - 2),
        ]

        pygame.draw.polygon(surface, (60, 100, 220), outer)
        pygame.draw.polygon(surface, (140, 180, 255), inner)
        pygame.draw.polygon(surface, WHITE, outer, 2)

        pygame.draw.line(surface, WHITE, (cx, cy - h // 2 + 6), (cx, cy + 2), 2)
        pygame.draw.line(surface, WHITE,
                         (cx - w // 2 + 6, cy - h // 4),
                         (cx + w // 2 - 6, cy - h // 4), 2)

    def apply(self, player):
        player.has_shield = True


class LaserPowerUp(PowerUp):
    COLLECT_RADIUS = 20
    LOW_COLOR     = (255, 80, 80)

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

    def apply(self, player):
        player.has_laser = True
