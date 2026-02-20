from enum import Enum, auto
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import NoteDirection

class ReceptorState(Enum):
    """
    Estados posibles del receptor (lane / key receptor).

    El receptor funciona como una pequeña máquina de estados (FSM)
    que controla qué debe dibujarse y cómo debe comportarse la animación.
    """
    IDLE = auto()
    HOLD_HIT = auto()      # Animación confirm, frame 0 congelado
    HOLD_MISS = auto()     # Imagen miss estática
    RELEASE_HIT = auto()   # Animación confirm completa
    RELEASE_MISS = auto()  # Transición de vuelta a static

@dataclass
class ReceptorFSM:
    state: ReceptorState = ReceptorState.IDLE
    direction: "NoteDirection | None" = None
    timer: float = 0.0