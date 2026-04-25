import math
import random

import pygame

from billo.settings import WIDTH, HEIGHT, BLUE, WHITE, GRAY, RED, GREEN

from billo.systems.fonts import font_large, font_mid, font_small

from billo.systems.sounds import create_sound_map

from billo.entities.bullets import Bullet
from billo.weapons.smg import SMGBullet
from billo.weapons.shotgun import ShotgunBullet

class Player:
    BASE_COOLDOWN = 30   # Default-Pistole Basis-Cooldown (50% langsamer als vorher)

    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 16
        self.speed = 4
        self.hp = 100
        self.max_hp = 100
        self.xp  = 0   # Gesammelte Erfahrungspunkte
        self.angle = 0          # Blickrichtung zur Maus
        self.shoot_cooldown = 0
        self.invincible     = 0  # Frames Unverwundbarkeit (60 = 1 Sek.)
        self.hit_flash      = 0  # Frames roter Treffer-Overlay
        self.shoot_speed_mult = 1.0   # Multiplikator: je höher, desto schneller
        self.powerup_level    = 0     # Anzahl eingesammelter PowerUps
        self.has_laser        = False  # Laserwaffe aktiv?
        self.laser_active     = False  # Wird Laser gerade abgefeuert?
        self.laser_damage_timer = 0    # Zählt hoch bis TICK_FRAMES
        self.laser_tick_mult  = 1.0   # Schadenstakt-Multiplikator (BulletTime)
        # --- SMG ---
        self.has_smg          = False  # SMG aktiv?
        # --- Shotgun ---
        self.has_shotgun      = False  # Shotgun aktiv?
        # --- Schaden ---
        self.damage_mult      = 1.0   # Multiplikator für Waffenschaden (stapelbar)
        self.damage_level     = 0     # Anzahl eingesammelter DamageUp-Items
        # --- Projektilgröße ---
        self.size_mult        = 1.0   # Multiplikator für Projektil-/Laserbreite
        self.size_level       = 0     # Anzahl eingesammelter GetsBigger-Items
        # --- Schild ---
        self.has_shield       = False  # Schutzschild aktiv?
        self.shield_pulse     = 0.0   # Puls-Animation-Phase
        # --- Dash ---
        self.dash_available   = True  # einmal pro Welle
        self.dash_timer       = 0     # Frames, die der Dash noch läuft (0 = inaktiv)
        self.dash_dx          = 0.0   # Dash-Richtungsvektor
        self.dash_dy          = 0.0
        self.dash_speed       = 18    # Pixel pro Frame während Dash
        self.dash_duration    = 14    # Frames Dash-Dauer (~0.23 s)
        self.ghost_trail      = []    # [(x, y, alpha)] für Nachzieh-Effekt

        self.sounds = create_sound_map()

    def update(self, keys):
        # --- Ghost-Trail altern ---
        self.ghost_trail = [(gx, gy, a - 18) for gx, gy, a in self.ghost_trail if a > 18]

        if self.dash_timer > 0:
            # Während Dash: feste Richtung, hohe Geschwindigkeit, unverwundbar
            self.x = max(self.radius, min(WIDTH  - self.radius, self.x + self.dash_dx * self.dash_speed))
            self.y = max(self.radius, min(HEIGHT - self.radius, self.y + self.dash_dy * self.dash_speed))
            self.ghost_trail.append((self.x, self.y, 200))
            self.dash_timer  -= 1
            self.invincible   = max(self.invincible, self.dash_timer + 1)
        else:
            dx = dy = 0
            if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= self.speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += self.speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= self.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += self.speed

            # Diagonale normalisieren
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707

            self.x = max(self.radius, min(WIDTH  - self.radius, self.x + dx))
            self.y = max(self.radius, min(HEIGHT - self.radius, self.y + dy))

        # Blickrichtung zur Maus
        mx, my = pygame.mouse.get_pos()
        self.angle = math.atan2(my - self.y, mx - self.x)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.laser_active:
            self.laser_damage_timer += 1
        if self.has_shield:
            self.shield_pulse += 0.08

    def try_dash(self, keys):
        """Startet den Dash in Bewegungsrichtung (oder Blickrichtung falls still)."""
        if not self.dash_available or self.dash_timer > 0:
            return
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if dx == 0 and dy == 0:
            # Kein Input → in Blickrichtung dashen
            dx = math.cos(self.angle)
            dy = math.sin(self.angle)
        dist = math.hypot(dx, dy)
        self.dash_dx      = dx / dist
        self.dash_dy      = dy / dist
        self.dash_timer   = self.dash_duration
        self.dash_available = False

    def reset_dash(self):
        self.dash_available = True

    def draw(self, surface):
        # --- Ghost-Trail (Nachziehspur beim Dash) ---
        for gx, gy, a in self.ghost_trail:
            ghost_surf = pygame.Surface((self.radius * 2 + 4, self.radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ghost_surf, (80, 200, 255, int(a)),
                               (self.radius + 2, self.radius + 2), self.radius)
            surface.blit(ghost_surf, (int(gx) - self.radius - 2, int(gy) - self.radius - 2))

        # Während Dash: Cyan-Leuchtring
        if self.dash_timer > 0:
            glow_r = self.radius + 8
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            glow_alpha = int(180 * self.dash_timer / self.dash_duration)
            pygame.draw.circle(glow_surf, (100, 220, 255, glow_alpha), (glow_r, glow_r), glow_r)
            surface.blit(glow_surf, (int(self.x) - glow_r, int(self.y) - glow_r))

        # Während Unverwundbarkeit (durch Treffer): Charakter blinkt
        if self.invincible > 0 and self.dash_timer == 0 and (self.invincible // 4) % 2 == 0:
            return
        # Körper
        color = (80, 220, 255) if self.dash_timer > 0 else BLUE
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        # Waffenlauf
        gun_len = 22
        ex = self.x + math.cos(self.angle) * gun_len
        ey = self.y + math.sin(self.angle) * gun_len
        barrel_color = (255, 60, 60) if self.has_laser else (255, 160, 30) if self.has_smg else (180, 130, 60) if self.has_shotgun else GRAY
        pygame.draw.line(surface, barrel_color, (int(self.x), int(self.y)), (int(ex), int(ey)), 5)

        # Schimmernder Schutzschild-Ring
        if self.has_shield:
            sr = self.radius + 10
            # Äußerer Glow pulsiert
            pulse_alpha = int(120 + 80 * math.sin(self.shield_pulse))
            glow_size = sr + 8
            shield_glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_glow, (100, 180, 255, pulse_alpha),
                               (glow_size, glow_size), glow_size)
            surface.blit(shield_glow, (int(self.x) - glow_size, int(self.y) - glow_size))
            # Harter Kreisrand
            shimmer = int(200 + 55 * math.sin(self.shield_pulse * 1.3))
            pygame.draw.circle(surface, (shimmer, shimmer, 255),
                               (int(self.x), int(self.y)), sr, 3)
            # Rotierender Glanzpunkt
            gp_angle = self.shield_pulse * 1.5
            gpx = int(self.x + math.cos(gp_angle) * sr)
            gpy = int(self.y + math.sin(gp_angle) * sr)
            pygame.draw.circle(surface, WHITE, (gpx, gpy), 4)

    def draw_hud(self, surface):
        # HP-Bar
        bar_w = 160
        bar_h = 16
        bx, by = 20, HEIGHT - 36
        pygame.draw.rect(surface, RED,   (bx, by, bar_w, bar_h))
        pygame.draw.rect(surface, GREEN, (bx, by, int(bar_w * self.hp / self.max_hp), bar_h))
        pygame.draw.rect(surface, WHITE, (bx, by, bar_w, bar_h), 2)
        hp_text = font_small.render(f"HP {self.hp}", True, WHITE)
        surface.blit(hp_text, (bx + bar_w + 10, by))

        # Dash-Indikator
        dash_color  = (80, 220, 255) if self.dash_available else (60, 80, 100)
        dash_label  = "DASH [SPACE]" if self.dash_available else "DASH verbraucht"
        dash_surf   = font_small.render(dash_label, True, dash_color)
        surface.blit(dash_surf, (bx, by - 24))
        # Kleines Icon-Rechteck
        pygame.draw.rect(surface, dash_color, (bx + dash_surf.get_width() + 8, by - 21, 14, 14), border_radius=3)
        if self.dash_available:
            pygame.draw.rect(surface, WHITE, (bx + dash_surf.get_width() + 8, by - 21, 14, 14), 2, border_radius=3)

        # Laser-Indikator
        if self.has_laser:
            laser_surf = font_small.render("🔴 LASER aktiv", True, (255, 80, 80))
            surface.blit(laser_surf, (bx, by - 46))

        # SMG-Indikator
        if self.has_smg:
            smg_surf = font_small.render("🟠 SMG aktiv", True, (255, 160, 30))
            surface.blit(smg_surf, (bx, by - 46))

        # Shotgun-Indikator
        if self.has_shotgun:
            sg_surf = font_small.render("🟤 SHOTGUN aktiv", True, (200, 140, 60))
            surface.blit(sg_surf, (bx, by - 46))

        # Schild-Indikator
        if self.has_shield:
            shield_surf = font_small.render("🛡 SCHILD aktiv", True, (140, 180, 255))
            surface.blit(shield_surf, (bx, by - 68))

        # DamageUp-Indikator
        if self.damage_level > 0:
            dmg_surf = font_small.render(f"💥 DMG +{self.damage_level * 2}%", True, (255, 100, 100))
            surface.blit(dmg_surf, (bx, by - 90))

    def shoot(self):
        if self.shoot_cooldown == 0:
            if self.has_smg:
                self.shoot_cooldown = max(1, int(self.BASE_COOLDOWN * 0.5 / self.shoot_speed_mult))
                random.choice(self.sounds["pews"]).play()
                return [SMGBullet(self.x, self.y, self.angle, self.size_mult)]
            elif self.has_shotgun:
                # 3 Pellets mit je ±15° Streuung
                self.shoot_cooldown = max(1, int(self.BASE_COOLDOWN * 1.5 / self.shoot_speed_mult))
                random.choice(self.sounds["pews"]).play()
                spread = math.radians(15)
                return [
                    ShotgunBullet(self.x, self.y, self.angle - spread, self.size_mult),
                    ShotgunBullet(self.x, self.y, self.angle,           self.size_mult),
                    ShotgunBullet(self.x, self.y, self.angle + spread, self.size_mult),
                ]
            else:
                self.shoot_cooldown = max(1, int(self.BASE_COOLDOWN / self.shoot_speed_mult))
                random.choice(self.sounds["pews"]).play()
                return [Bullet(self.x, self.y, self.angle, self.size_mult)]
        return []

    def collect_powerup(self):
        self.powerup_level    += 1
        self.shoot_speed_mult *= 1.02   # +2 % Schussrate für Bullet-Waffen
        self.laser_tick_mult  *= 1.02   # +2 % Tick-Rate für Laser

    def collect_laser_powerup(self):
        self.has_laser   = True
        self.has_smg     = False
        self.has_shotgun = False

    def collect_smg_pickup(self):
        self.has_smg     = True
        self.has_laser   = False
        self.has_shotgun = False

    def collect_shotgun_pickup(self):
        self.has_shotgun = True
        self.has_laser   = False
        self.has_smg     = False

    def collect_shield_powerup(self):
        self.has_shield   = True
        self.shield_pulse = 0.0

    def collect_damageup(self):
        self.damage_level += 1
        self.damage_mult  *= 1.02   # +2 % pro Stack

    def collect_getsbigger(self):
        self.size_level += 1
        self.size_mult  *= 1.03   # +3 % pro Stack
