import math
import random
import pygame

from billo.settings import WIDTH, HEIGHT, DARK_GREEN, BLACK, WHITE, ORANGE, RED, YELLOW

from billo.weapons.laser import Laser
from billo.systems.fonts import font_mid, font_large, font_small


class Renderer:
    """Zuständig für alles Visuelle – kein Spielzustand wird hier verändert."""

    def __init__(self, screen):
        self.screen = screen

    def draw(self, game):
        # Screen-Shake
        if game.shake_timer > 0:
            game.shake_timer -= 1
            intensity = min(game.shake_timer, 8)
            ox = random.randint(-intensity, intensity)
            oy = random.randint(-intensity, intensity)
        else:
            ox = oy = 0

        surface = pygame.Surface((WIDTH, HEIGHT))
        _draw_background(surface)

        for p in game.particles:
            p.draw(surface)
        for pu in game.powerups:
            pu.draw(surface)
        for lpu in game.laser_pickups:
            lpu.draw(surface)
        for spu in game.smg_pickups:
            spu.draw(surface)
        for sgpu in game.shotgun_pickups:
            sgpu.draw(surface)
        for spu in game.shield_powerups:
            spu.draw(surface)
        for du in game.damageups:
            du.draw(surface)
        for gb in game.getsbiggers:
            gb.draw(surface)
        for t in game.trinkets:
            t.draw(surface)
        for orb in game.xporbs:
            orb.draw(surface)
        for z in game.zombies:
            z.draw(surface)
        for b in game.bullets:
            b.draw(surface)

        if game.player.laser_active:
            laser = Laser(game.player.x, game.player.y, game.player.angle)
            laser.draw(surface, game.frame, game.player.size_mult)

        game.player.draw(surface)
        # Orbital-Satelliten
        for sat in getattr(game.player, "satellites", []):
            sat.draw(surface, game.player.x, game.player.y)
        game.player.draw_hud(surface)

        # ── Score & Welle ──
        score_surf = font_mid.render(f"Score: {game.score}", True, WHITE)
        wave_surf  = font_mid.render(f"Welle: {game.wave}",  True, ORANGE)
        surface.blit(score_surf, (20, 16))
        surface.blit(wave_surf,  (20, 44))

        # ── XP oben rechts ──
        xp_surf = font_mid.render(f"XP: {game.player.xp}", True, (120, 255, 180))
        surface.blit(xp_surf, (WIDTH - xp_surf.get_width() - 20, 16))

        # ── Wellen-Timer / Zwischen-Wellen-Banner ──
        if game.between_waves:
            _draw_between_banner(surface, game)
        else:
            _draw_wave_timer(surface, game)

        # ── Pause-Overlay ──
        if game.paused:
            _draw_pause_overlay(surface, game)

        self.screen.fill(BLACK)
        self.screen.blit(surface, (ox, oy))
        pygame.display.flip()


def _draw_wave_timer(surface, game):
    """Zeigt verbleibende Wellenzeit als Balken + Sekunden oben mittig."""
    fps       = 60
    secs_left = max(0, math.ceil(game.wave_frames_left / fps))
    total     = (10 + (game.wave - 1) * 5)   # Gesamtdauer in Sekunden

    # Farbe wechselt zu Rot wenn < 5 Sekunden
    color = RED if secs_left <= 5 else ORANGE

    # Sekunden-Text
    timer_surf = font_mid.render(f"⏱ {secs_left}s", True, color)
    tx = WIDTH // 2 - timer_surf.get_width() // 2
    surface.blit(timer_surf, (tx, 16))

    # Fortschrittsbalken
    bar_w  = 300
    bar_h  = 10
    bx     = WIDTH // 2 - bar_w // 2
    by     = 52
    fill_w = int(bar_w * (game.wave_frames_left / (total * fps)))
    pygame.draw.rect(surface, (60, 60, 60),   (bx, by, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surface, color,           (bx, by, max(0, fill_w), bar_h), border_radius=4)
    pygame.draw.rect(surface, WHITE,           (bx, by, bar_w, bar_h), 2, border_radius=4)


def _draw_between_banner(surface, game):
    """Zeigt das Zwischen-Wellen-Banner mit Countdown."""
    fps       = 60
    secs_left = max(0, math.ceil(game.between_timer / fps))

    # Halbtransparentes dunkles Overlay
    overlay = pygame.Surface((WIDTH, 160), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, HEIGHT // 2 - 80))

    next_wave = game.wave + 1
    title_surf = font_large.render(f"Welle {next_wave} beginnt in {secs_left}s", True, YELLOW)
    sub_surf   = font_small.render("Sammle Pickups ein!", True, WHITE)

    surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 2 - 50))
    surface.blit(sub_surf,   (WIDTH // 2 - sub_surf.get_width()   // 2, HEIGHT // 2 + 20))


def _draw_background(surface):
    surface.fill(DARK_GREEN)
    for gx in range(0, WIDTH, 40):
        pygame.draw.line(surface, (0, 60, 0), (gx, 0), (gx, HEIGHT))
    for gy in range(0, HEIGHT, 40):
        pygame.draw.line(surface, (0, 60, 0), (0, gy), (WIDTH, gy))

def _draw_pause_overlay(surface, game):
    """Halbtransparentes Pause-Menü mit gesammelten Powerups."""
    p = game.player

    # Dunkles Overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    # Panel
    panel_w, panel_h = 1040, 440
    px = WIDTH  // 2 - panel_w // 2
    py = HEIGHT // 2 - panel_h // 2
    pygame.draw.rect(surface, (25, 25, 40),  (px, py, panel_w, panel_h), border_radius=12)
    pygame.draw.rect(surface, (140, 80, 255), (px, py, panel_w, panel_h), 2, border_radius=12)

    # Titel
    title = font_large.render("⏸  PAUSE", True, (180, 120, 255))
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, py + 20))

    # Trennlinie
    pygame.draw.line(surface, (80, 50, 140),
                     (px + 20, py + 80), (px + panel_w - 20, py + 80), 1)

    # ── Powerups (immer anzeigen) ──
    items = []
    if p.powerup_level > 0:
        items.append(("🔵 BulletTime Stacks", f"{p.powerup_level}x  (+{round((p.shoot_speed_mult - 1) * 100, 1)}% Feuerrate)"))
    if p.damage_level > 0:
        items.append(("💥 DamageUp Stacks",   f"{p.damage_level}x  (+{round((p.damage_mult - 1) * 100, 1)}% Schaden)"))
    if p.size_level > 0:
        items.append(("🟢 GetsBigger Stacks", f"{p.size_level}x  (+{round((p.size_mult - 1) * 100, 1)}% Projektilgröße)"))
    if p.has_shield:
        items.append(("🛡 Schild", "Aktiv"))

    # ── Aktive Waffe ──
    if p.has_laser:
        items.append(("🔴 Laser", "Ausgerüstet"))
    elif p.has_smg:
        items.append(("🟠 SMG", "Ausgerüstet"))
    elif p.has_shotgun:
        items.append(("🟤 Shotgun", "Ausgerüstet"))
    else:
        items.append(("🔫 Pistole", "Ausgerüstet"))

    # ── Aktive Trinkets ──
    if getattr(p, "has_swiftness", False):
        items.append(("⚡ Swiftness", "Aktiv  (+15% Geschwindigkeit)"))
    sat_count = len(getattr(p, "satellites", []))
    if sat_count > 0:
        items.append(("🔮 OrbitalMiniME", f"{sat_count}x Satellit aktiv"))

    # Fallback wenn gar nichts gesammelt
    if not items:
        items.append(("—", "Noch keine Items gesammelt"))

    y = py + 100
    for label, value in items:
        label_s = font_mid.render(label, True, (200, 200, 220))
        value_s = font_mid.render(value, True, (255, 220, 80))
        surface.blit(label_s, (px + 30, y))
        surface.blit(value_s, (px + panel_w - value_s.get_width() - 30, y))
        y += 48

    # Trennlinie
    pygame.draw.line(surface, (80, 50, 140),
                     (px + 20, y + 8), (px + panel_w - 20, y + 8), 1)

    # Hinweis
    hint = font_small.render("[TAB]  –  Spiel fortsetzen", True, (140, 140, 160))
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, py + panel_h - 36))




