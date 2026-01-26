from src.core.game import Game
import pygame

if not pygame.get_init():
    pygame.init()

game = Game("Keep The Cadence")

if __name__ == "__main__":
    game.run()
