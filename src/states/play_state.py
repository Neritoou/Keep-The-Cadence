import pygame
from typing import TYPE_CHECKING
from .game_state import GameState
from ..core import OverlayType
from .state_id import StateID

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

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE

    @property
    def is_transient(self) -> bool:
        return False