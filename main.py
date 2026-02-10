from enfocate import GameMetadata
from src.core.game import Game
import pygame

if not pygame.get_init():
    pygame.init()

meta = GameMetadata(
                title="Keep The Cadence",
                description="Juego de Ritmo inspirado en Friday Night Funkin.",
                authors=["Odett Sayegh", "Agostinho Dos Santos"],
                group_number=4
            )

game = Game(meta)

if __name__ == "__main__":
    game.run_preview()
