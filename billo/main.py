import pygame

from billo.game import Game
from billo.renderer import Renderer
from billo.settings import WIDTH, HEIGHT, RED, YELLOW, GRAY, WHITE
from billo.systems.fonts import font_large, font_mid


def setup():
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    return screen, clock


def start_screen(screen):
    while True:
        screen.fill((10, 20, 10))
        title = font_large.render("ZOMBIE SURVIVAL", True, RED)
        sub   = font_mid.render("WASD bewegen  |  Maus zielen  |  Klick schießen  |  SPACE dashen", True, GRAY)
        start = font_mid.render("[ LEERTASTE zum Starten ]", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))
        screen.blit(sub,   (WIDTH // 2 - sub.get_width()   // 2, 280))
        screen.blit(start, (WIDTH // 2 - start.get_width() // 2, 360))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return


def game_over_screen(score, screen):
    while True:
        screen.fill((10, 0, 0))
        title  = font_large.render("GAME OVER", True, RED)
        s_surf = font_mid.render(f"Score: {score}", True, WHITE)
        retry  = font_mid.render("[ LEERTASTE für Neustart  |  ESC zum Beenden ]", True, GRAY)
        screen.blit(title,  (WIDTH // 2 - title.get_width()  // 2, 180))
        screen.blit(s_surf, (WIDTH // 2 - s_surf.get_width() // 2, 280))
        screen.blit(retry,  (WIDTH // 2 - retry.get_width()  // 2, 360))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  return True
                if event.key == pygame.K_ESCAPE: pygame.quit()


def run():
    screen, clock = setup()
    game     = Game()
    renderer = Renderer(screen)

    start_screen(screen)

    while True:
        clock.tick(60)
        keys  = game.handle_events()
        alive = game.update(keys)
        renderer.draw(game)

        if not alive:
            game_over_screen(game.score, screen)
            game.reset()
