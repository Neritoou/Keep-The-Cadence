from enum import Enum, auto
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import NoteDirection

class NoteReceptorState(Enum):
    IDLE = auto()
    HOLD_HIT = auto()
    HOLD_MISS = auto()
    RELEASE_HIT = auto()
    RELEASE_MISS = auto()

class CharacterReceptorState(Enum):
    IDLE = auto()
    HOLD_HIT = auto()
    HOLD_MISS = auto()
    RELEASE_HIT = auto()
    RELEASE_MISS = auto()
    WIN = auto()

# FSM genérica — acepta cualquier Enum
@dataclass
class ReceptorFSM:
    state: Enum
    direction: "NoteDirection | None" = None
    timer: float = 0.0