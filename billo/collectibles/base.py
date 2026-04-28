import json
import random
import math
import pygame

from billo.settings import WIDTH, HEIGHT


class Collectible:
    COLLECT_RADIUS = 20
    GLOW_COLOR     = (255, 255, 255)

    BOB_AMPLITUDE  = 3
    BOB_SPEED      = 0.07
    MARGIN         = 60
    RARITY         = 0.03

    def __init__(self):
        self.x = random.randint(self.MARGIN, WIDTH  - self.MARGIN)
        self.y = random.randint(self.MARGIN, HEIGHT - self.MARGIN)

        self.alive = True
        self.bob_t = random.uniform(0, 2 * math.pi)

    def update(self):
        self.bob_t += self.BOB_SPEED

    def get_draw_pos(self):
        bob_y = int(self.y + math.sin(self.bob_t) * self.BOB_AMPLITUDE)
        return int(self.x), bob_y

    def draw_glow(self, surface, cx, cy):
        glow_r = self.COLLECT_RADIUS + 4

        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha = int(60 + 30 * math.sin(self.bob_t * 2))

        r, g, b = self.GLOW_COLOR
        pygame.draw.circle(glow, (r, g, b, alpha), (glow_r, glow_r), glow_r)

        surface.blit(glow, (cx - glow_r, cy - glow_r))

    def draw(self, surface):
        cx, cy = self.get_draw_pos()
        self.draw_glow(surface, cx, cy)
        self.draw_icon(surface, cx, cy)

    def draw_icon(self, surface, cx, cy):
        raise NotImplementedError

    def on_collect(self, player):
        """Unified hook (replaces apply)."""
        raise NotImplementedError


class CollectibleRegistry:
    def __init__(self):
        self._data = {}

    def load(self, path):
        with open(path, "r") as f:
            self._data = json.load(f)

    def get(self, key):
        return self._data[key]

    def all_keys(self):
        return list(self._data.keys())


class JSONCollectible(Collectible):
    def __init__(self, data):
        super().__init__()

        self.data = data

        self.glow_color = tuple(data.get("glow_color", (255, 255, 255)))
        self.icon       = data.get("icon", "circle")
        self.effects    = data.get("effects", [])
        self.stackable  = data.get("stackable", True)
        self.unlock     = data.get("unlock")

    def draw_icon(self, surface, cx, cy):
        if self.icon == "circle":
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 6)

        elif self.icon == "bullet":
            pygame.draw.rect(surface, (180, 40, 40),
                             (cx - 5, cy - 10, 10, 20), border_radius=3)

        elif self.icon == "bullet_gold":
            pygame.draw.rect(surface, (210, 170, 30),
                             (cx - 5, cy - 10, 10, 20), border_radius=3)

        elif self.icon == "star":
            for i in range(5):
                angle = i * (2 * math.pi / 5)
                x = cx + math.cos(angle) * 10
                y = cy + math.sin(angle) * 10
                pygame.draw.line(surface, (255, 160, 30),
                                 (cx, cy), (x, y), 2)

        elif self.icon == "bolt":
            pygame.draw.line(surface, (255, 230, 50),
                             (cx - 3, cy - 10), (cx + 3, cy + 10), 3)

    def on_collect(self, player):
        if self.unlock:
            if not hasattr(player, "weapons_unlocked"):
                player.weapons_unlocked = set()
            player.weapons_unlocked.add(self.unlock)

        for effect in self.effects:
            stat = effect["stat"]
            op   = effect["op"]
            val  = effect["value"]

            current = getattr(player, stat)

            if op == "mul":
                setattr(player, stat, current * val)

            elif op == "add":
                setattr(player, stat, current + val)

        if not self.stackable:
            key = self.data.get("_id")
            if not hasattr(player, "_collected"):
                player._collected = set()

            if key in player._collected:
                return
            player._collected.add(key)


class CollectibleFactory:
    def __init__(self, registry):
        self.registry = registry

    def create(self, key):
        base = deepcopy(self.registry.get(key))
        base["_id"] = key

        for eff in base.get("effects", []):
            if eff["op"] == "mul":
                eff["value"] *= random.uniform(0.95, 1.05)

        if "glow_color" in base:
            r, g, b = base["glow_color"]
            base["glow_color"] = [
                min(255, max(0, r + random.randint(-10, 10))),
                min(255, max(0, g + random.randint(-10, 10))),
                min(255, max(0, b + random.randint(-10, 10)))
            ]
        if random.random() < 0.05:
            for eff in base.get("effects", []):
                eff["value"] *= 1.5  # jackpot version

        return JSONCollectible(base)
