import math

import pygame

from billo.settings import WIDTH, HEIGHT, DARK_GREEN, RED, WHITE, ORANGE, BLACK

from billo.entities.player import Player
from billo.entities.zombies import Zombie
from billo.entities.bullets import Bullet
from billo.entities.particles import Particle

from billo.systems.sounds import make_laser_sound, make_pew_sound
from billo.systems.fonts import font_small, font_mid, font_large

class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.sounds = {
                "LASER_SOUND": make_laser_sound(.25),
                "PEW_SOUNDS": [
                    make_pew_sound(freq_start=1000, freq_end=250, duration=0.07),
                    make_pew_sound(freq_start=850,  freq_end=200, duration=0.09),
                    make_pew_sound(freq_start=1100, freq_end=300, duration=0.06),
                ]
            }

        self.reset()

    def reset(self):
        self.player    = Player()
        self.bullets   = []
        self.zombies   = []
        self.particles = []

        self.powerups        = []
        self.laser_powerups  = []
        self.shield_powerups = []

        self.score = 0
        self.wave  = 1

        self.wave_timer       = 0
        self.wave_spawn_delay = 120
        self.zombies_per_wave = 5

        self.shake_timer = 0
        self.frame       = 0

        # erste Welle
        for _ in range(self.zombies_per_wave):
            self.zombies.append(Zombie(self.wave))

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

        # Dauerfeuer
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

        # Zombies
        for z in self.zombies:
            z.update(self.player.x, self.player.y)

        # Bullet collisions
        for b in self.bullets:
            for z in self.zombies:
                if z.alive and math.hypot(b.x - z.x, b.y - z.y) < b.radius + z.radius:
                    b.alive = False
                    killed = z.hit(25)

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

        # Waves
        if len(self.zombies) == 0:
            self.wave_timer += 1
            if self.wave_timer >= self.wave_spawn_delay:
                self.wave += 1
                self.wave_timer = 0
                self.zombies_per_wave += 3

                for _ in range(self.zombies_per_wave):
                    self.zombies.append(Zombie(self.wave))

                self.player.reset_dash()

                if random.random() < 0.20:
                    self.powerups.append(PowerUp())

                if not self.player.has_laser and random.random() < 0.20:
                    self.laser_powerups.append(LaserPowerUp())

                if not self.player.has_shield and random.random() < 0.20:
                    self.shield_powerups.append(ShieldPowerUp())

        # Powerups
        for pu in self.powerups:
            pu.update()
            if math.hypot(self.player.x - pu.x, self.player.y - pu.y) < pu.COLLECT_RADIUS + self.player.radius:
                self.player.collect_powerup()
                pu.alive = False

        self.powerups = [p for p in self.powerups if p.alive]

        # Laser damage
        if self.player.laser_active and self.player.laser_damage_timer >= Laser.TICK_FRAMES:
            self.player.laser_damage_timer = 0

            for z in self.zombies:
                if z.alive and Laser.ray_hits_circle(
                    self.player.x, self.player.y, self.player.angle,
                    z.x, z.y, z.radius
                ):
                    killed = z.hit(Laser.DAMAGE)
                    if killed:
                        self.score += 10

        # Laser powerups
        for lpu in self.laser_powerups:
            lpu.update()
            if math.hypot(self.player.x - lpu.x, self.player.y - lpu.y) < lpu.COLLECT_RADIUS + self.player.radius:
                self.player.collect_laser_powerup()
                lpu.alive = False

        self.laser_powerups = [l for l in self.laser_powerups if l.alive]

        # Shield powerups
        for spu in self.shield_powerups:
            spu.update()
            if math.hypot(self.player.x - spu.x, self.player.y - spu.y) < spu.COLLECT_RADIUS + self.player.radius:
                self.player.collect_shield_powerup()
                spu.alive = False

        self.shield_powerups = [s for s in self.shield_powerups if s.alive]

        # Game Over
        if self.player.hp <= 0:
            self.sounds["LASER_SOUND"].stop()
            return False

        return True

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            intensity = min(self.shake_timer, 8)
            ox = random.randint(-intensity, intensity)
            oy = random.randint(-intensity, intensity)
        else:
            ox = oy = 0

        surface = pygame.Surface((WIDTH, HEIGHT))
        draw_background(surface)

        for p in self.particles:
            p.draw(surface)
        for pu in self.powerups:
            pu.draw(surface)
        for lpu in self.laser_powerups:
            lpu.draw(surface)
        for spu in self.shield_powerups:
            spu.draw(surface)
        for z in self.zombies:
            z.draw(surface)
        for b in self.bullets:
            b.draw(surface)

        if self.player.laser_active:
            laser = Laser(self.player.x, self.player.y, self.player.angle)
            laser.draw(surface, self.frame)

        self.player.draw(surface)
        self.player.draw_hud(surface)

        score_surf = font_mid.render(f"Score: {self.score}", True, WHITE)
        wave_surf  = font_mid.render(f"Welle: {self.wave}", True, ORANGE)

        surface.blit(score_surf, (20, 16))
        surface.blit(wave_surf,  (20, 44))

        self.screen.fill(BLACK)
        self.screen.blit(surface, (ox, oy))
        pygame.display.flip()

    # -------------------------
    # MAIN LOOP
    # -------------------------
    def run(self):
        while True:
            self.clock.tick(60)

            keys = self.handle_events()
            alive = self.update(keys)
            self.draw()

            if not alive:
                return self.score

def draw_background(surface):
    surface.fill(DARK_GREEN)
    for gx in range(0, WIDTH, 40):
        pygame.draw.line(surface, (0, 60, 0), (gx, 0), (gx, HEIGHT))
    for gy in range(0, HEIGHT, 40):
        pygame.draw.line(surface, (0, 60, 0), (0, gy), (WIDTH, gy))

