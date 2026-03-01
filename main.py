from src.core.game import Game
import pygame

if not pygame.get_init():
    pygame.init()

game = Game()

if __name__ == "__main__":
    game.run_preview()