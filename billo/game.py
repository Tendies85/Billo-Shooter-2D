import sys
import math
import random

import pygame

from billo.entities.player import Player
from billo.entities.zombies import Zombie
from billo.entities.particles import Particle

from billo.weapons.laser import Laser, LaserWeaponPickUp
from billo.weapons.smg import SMGBullet, SMGPickUp

from billo.powerups.powerup import BulletTime
from billo.powerups.shield import ShieldPowerUp
from billo.powerups.damageup import DamageUp

from billo.systems.sounds import make_laser_sound, make_pew_sound

from billo.trinkets import TRINKET_POOL

FPS               = 60
WAVE_BASE_SECS    = 10   # Welle 1 dauert 10 Sekunden
WAVE_EXTRA_SECS   = 5    # jede weitere Welle +5 Sekunden
ZOMBIE_SPAWN_SECS = 1    # alle 1 Sekunde ein neuer Zombie (50% häufiger)
ITEM_SPAWN_SECS   = 8    # alle 8 Sekunden ein zufälliges Item


class Game:
    """Reine Spiellogik – kein pygame.draw, kein Surface, kein Bildschirm."""

    def __init__(self):
        self.sounds = {
            "LASER_SOUND": make_laser_sound(.25),
            "PEW_SOUNDS": [
                make_pew_sound(freq_start=1000, freq_end=250, duration=0.07),
                make_pew_sound(freq_start=850,  freq_end=200, duration=0.09),
                make_pew_sound(freq_start=1100, freq_end=300, duration=0.06),
            ]
        }
        self.reset()

    # ------------------------------------------------------------------
    # Hilfsmethode: Wellendauer in Frames
    # ------------------------------------------------------------------
    def _wave_duration(self, wave):
        return (WAVE_BASE_SECS + (wave - 1) * WAVE_EXTRA_SECS) * FPS

    def reset(self):
        self.player    = Player()
        self.bullets   = []
        self.zombies   = []
        self.particles = []

        self.powerups        = []
        self.laser_pickups   = []
        self.smg_pickups     = []
        self.shield_powerups = []
        self.damageups       = []
        self.trinkets        = []

        self.score = 0
        self.wave  = 1

        # Zeitbasiertes Wellensystem
        self.wave_frames_left  = self._wave_duration(1)  # verbleibende Frames
        self.zombie_spawn_timer = 0                       # Frames seit letztem Spawn
        self.item_spawn_timer   = 0                       # Frames seit letztem Item-Spawn
        self.between_waves     = False                    # kurze Pause zwischen Wellen
        self.between_timer     = 0
        self.between_duration  = 3 * FPS                 # 3 Sekunden Pause

        self.shake_timer = 0
        self.frame       = 0

        self.zombie_spawn_count = 1   # Anzahl Zombies pro Spawn-Intervall

        # Erste Zombies sofort spawnen
        self._spawn_zombie()

    # ------------------------------------------------------------------
    # Zombie am Bildschirmrand spawnen
    # ------------------------------------------------------------------
    def _spawn_zombie(self):
        for _ in range(self.zombie_spawn_count):
            self.zombies.append(Zombie(self.wave))


    # ------------------------------------------------------------------
    # Zufälliges Item während der laufenden Welle spawnen
    # ------------------------------------------------------------------
    def _spawn_item(self):
        if random.random() < 0.20:
            self.powerups.append(BulletTime())
        if not self.player.has_shield and random.random() < 0.20:
            self.shield_powerups.append(ShieldPowerUp())
        if random.random() < 0.20:
            self.damageups.append(DamageUp())
        if random.random() < 0.05:
            self.laser_pickups.append(LaserWeaponPickUp())
        if random.random() < 0.05:
            self.smg_pickups.append(SMGPickUp())
        if random.random() < 0.03:
            trinket_cls = random.choice(TRINKET_POOL)
            self.trinkets.append(trinket_cls())

    # ------------------------------------------------------------------
    # Welle beenden: alles leeren, Pickups spawnen, Pause starten
    # ------------------------------------------------------------------
    def _end_wave(self):
        self.between_waves = True
        self.between_timer = self.between_duration

        # Alle verbliebenen Gegner und Pickups entfernen
        self.zombies         = []
        self.bullets         = []
        self.powerups        = []
        self.shield_powerups = []
        self.damageups       = []
        self.laser_pickups   = []
        self.smg_pickups     = []
        self.trinkets        = []

        self.player.reset_dash()

    # ------------------------------------------------------------------
    # Nächste Welle starten
    # ------------------------------------------------------------------
    def _start_next_wave(self):
        self.wave += 1
        self.between_waves      = False
        self.wave_frames_left   = self._wave_duration(self.wave)
        self.zombie_spawn_timer = 0
        self.item_spawn_timer   = 0

        # Gegneranzahl pro Spawn um 10 % erhöhen
        self.zombie_spawn_count = max(1, round(self.zombie_spawn_count * 1.10))

        # Erster Zombie sofort
        self._spawn_zombie()

    # -------------------------
    # EVENT HANDLING
    # -------------------------
    def handle_events(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.player.has_laser:
                    b = self.player.shoot()
                    if b:
                        self.bullets.append(b)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.try_dash(keys)

        if not self.player.has_laser and pygame.mouse.get_pressed()[0]:
            b = self.player.shoot()
            if b:
                self.bullets.append(b)

        return keys

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, keys):
        self.player.update(keys)
        self.frame += 1

        # Laser handling
        if self.player.has_laser:
            self.player.laser_active = pygame.mouse.get_pressed()[0]
            if self.player.laser_active:
                self.sounds["LASER_SOUND"].set_volume(0.25)
                self.sounds["LASER_SOUND"].play(-1)
            else:
                self.sounds["LASER_SOUND"].stop()
        else:
            self.player.laser_active = False
            self.sounds["LASER_SOUND"].stop()

        # Bullets
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.alive]

        # ── Wellen-Logik ──────────────────────────────────────────────
        if self.between_waves:
            # Pause zwischen Wellen – Countdown
            self.between_timer -= 1
            if self.between_timer <= 0:
                self._start_next_wave()
        else:
            # Aktive Welle: Countdown und regelmäßiger Zombie-Spawn
            self.wave_frames_left  -= 1
            self.zombie_spawn_timer += 1

            if self.zombie_spawn_timer >= ZOMBIE_SPAWN_SECS * FPS:
                self.zombie_spawn_timer = 0
                self._spawn_zombie()

            self.item_spawn_timer += 1
            if self.item_spawn_timer >= ITEM_SPAWN_SECS * FPS:
                self.item_spawn_timer = 0
                self._spawn_item()

            if self.wave_frames_left <= 0:
                self._end_wave()

        # Zombies bewegen
        for z in self.zombies:
            z.update(self.player.x, self.player.y)

        # Bullet collisions
        for b in self.bullets:
            for z in self.zombies:
                if z.alive and math.hypot(b.x - z.x, b.y - z.y) < b.radius + z.radius:
                    b.alive = False
                    damage = SMGBullet.DAMAGE if isinstance(b, SMGBullet) else 25
                    damage = int(damage * self.player.damage_mult)
                    killed = z.hit(damage)
                    for _ in range(8):
                        self.particles.append(Particle(z.x, z.y, (180, 30, 30)))
                    if killed:
                        self.score += 10

        # Zombie → Player
        for z in self.zombies:
            if z.alive and self.player.invincible == 0:
                if math.hypot(self.player.x - z.x, self.player.y - z.y) < self.player.radius + z.radius:
                    if self.player.has_shield:
                        self.player.has_shield = False
                        self.player.invincible = 60
                        self.shake_timer = 10
                        for _ in range(20):
                            self.particles.append(Particle(self.player.x, self.player.y, (140, 180, 255)))
                    else:
                        self.player.hp -= 10
                        self.player.invincible = 60
                        self.player.hit_flash = 60
                        self.shake_timer = 18

        self.zombies = [z for z in self.zombies if z.alive]

        # Particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # Powerups (Schussrate)
        for pu in self.powerups:
            pu.update()
            if math.hypot(self.player.x - pu.x, self.player.y - pu.y) < pu.COLLECT_RADIUS + self.player.radius:
                self.player.collect_powerup()
                pu.alive = False
        self.powerups = [p for p in self.powerups if p.alive]

        # Laser damage
        effective_tick = max(1, int(Laser.TICK_FRAMES / self.player.laser_tick_mult))
        if self.player.laser_active and self.player.laser_damage_timer >= effective_tick:
            self.player.laser_damage_timer = 0
            for z in self.zombies:
                if z.alive and Laser.ray_hits_circle(
                    self.player.x, self.player.y, self.player.angle,
                    z.x, z.y, z.radius
                ):
                    killed = z.hit(Laser.DAMAGE)
                    if killed:
                        self.score += 10

        # Laser-Pickups
        for lpu in self.laser_pickups:
            lpu.update()
            if math.hypot(self.player.x - lpu.x, self.player.y - lpu.y) < lpu.COLLECT_RADIUS + self.player.radius:
                self.player.collect_laser_powerup()
                lpu.alive = False
        self.laser_pickups = [l for l in self.laser_pickups if l.alive]

        # SMG-Pickups
        for spu in self.smg_pickups:
            spu.update()
            if math.hypot(self.player.x - spu.x, self.player.y - spu.y) < spu.COLLECT_RADIUS + self.player.radius:
                self.player.collect_smg_pickup()
                spu.alive = False
        self.smg_pickups = [s for s in self.smg_pickups if s.alive]

        # Shield-Powerups
        for spu in self.shield_powerups:
            spu.update()
            if math.hypot(self.player.x - spu.x, self.player.y - spu.y) < spu.COLLECT_RADIUS + self.player.radius:
                self.player.collect_shield_powerup()
                spu.alive = False
        self.shield_powerups = [s for s in self.shield_powerups if s.alive]

        # DamageUp-Pickups
        for du in self.damageups:
            du.update()
            if math.hypot(self.player.x - du.x, self.player.y - du.y) < du.COLLECT_RADIUS + self.player.radius:
                self.player.collect_damageup()
                du.alive = False
        self.damageups = [d for d in self.damageups if d.alive]

        # Trinkets
        for t in self.trinkets:
            t.update()
            if math.hypot(self.player.x - t.x, self.player.y - t.y) < t.COLLECT_RADIUS + self.player.radius:
                t.apply(self.player)
                t.alive = False
        self.trinkets = [t for t in self.trinkets if t.alive]

        # Game Over
        if self.player.hp <= 0:
            self.sounds["LASER_SOUND"].stop()
            return False

        return True


