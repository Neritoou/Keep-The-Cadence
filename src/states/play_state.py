import pygame
from typing import TYPE_CHECKING

from pygame.event import Event
from .game_state import GameState
from .types import OverlayType

if TYPE_CHECKING:
    from src.core.game import Game


class PlayState(GameState):
    """
    Estado principal del juego donde ocurren todas las acciones del Tetris.

    Coordina la interacción entre el tablero (Board), el generador de piezas
    (PieceBag) y la entrada del usuario.
    """
    def __init__(self, game: "Game"):
        super().__init__(game)

    def on_exit(self) -> None:
        return super().on_exit()
    
    def handle_input(self, events: list[Event]) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass

    def update(self, dt: float) -> None:
        pass
    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE

    @property
    def is_transient(self) -> bool:
        return False