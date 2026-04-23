import pygame

from billo.game import Game
from billo.settings import WIDTH, HEIGHT

def setup():
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    return screen, clock

def run():
    screen, clock = setup()
    game = Game(screen, clock)

    while True:
        score = game.run()
        game_over_screen(score)
        game.reset()
