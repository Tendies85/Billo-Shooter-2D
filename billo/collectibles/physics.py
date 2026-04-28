import random
import math
import pygame

from billo.collectible import Collectible

class PhysicsCollectible(Collectible):
    """
    Collectible with velocity-based movement.

    Adds:
    - dx/dy velocity
    - friction
    - optional attraction behavior
    """

    def __init__(self, x=None, y=None):
        super().__init__()

        # allow manual spawn override
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

        self.dx = 0.0
        self.dy = 0.0
        self.friction = 0.9

    # ─────────────────────────────────────────

    def apply_velocity(self):
        self.x += self.dx
        self.y += self.dy

    def apply_friction(self):
        self.dx *= self.friction
        self.dy *= self.friction

    # ─────────────────────────────────────────

    def attract_to(self, tx, ty, speed, max_range):
        dist = math.hypot(tx - self.x, ty - self.y)

        if 0 < dist < max_range:
            self.dx = (tx - self.x) / dist * speed
            self.dy = (ty - self.y) / dist * speed
            return True

        return False

    # ─────────────────────────────────────────

    def update(self, player=None):
        """
        Default physics update:
        - bobbing (base)
        - friction
        - movement

        Subclasses can extend this.
        """
        super().update()

        self.apply_friction()
        self.apply_velocity()




