from enum import Enum, IntEnum, auto
from pygame import Surface
from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.types import NoteDirection

class JsonNoteData(TypedDict):
    """Representación JSON de una nota"""
    hitTime: float      # Tiempo cuando debe golpearse (ms)
    duration: float     # Duración de hold note (0 si es TAP)
    direction: int      # Dirección (0=LEFT, 1=DOWN, 2=UP, 3=RIGHT)

class JsonSectionData(TypedDict):
    """Representación JSON de una sección"""
    index: int          # Índice de la sección
    startTime: float    # Tiempo de inicio (ms)
    endTime: float      # Tiempo de fin (ms)
    notes: list[JsonNoteData]  # Lista de notas en la sección

class JsonChartData(TypedDict):
    """Representación JSON completa del chart"""
    song: str               # Path al archivo de audio
    bpm: int                # BPM de la canción
    pixels_per_ms: float            # Velocidad de scroll
    sections: list[JsonSectionData]  # Lista de secciones


class NoteDirection(IntEnum):
    """
    Direcciones de notas (como IntEnum para compatibilidad con índices).
    Los valores corresponden a índices de las flechas.
    """
    LEFT = 0
    DOWN = 1
    UP = 2
    RIGHT = 3

class ScrollDirection(Enum):
    """
    Dirección de scroll de las notas.
    El valor indica el multiplicador para el cálculo de posición Y.
    """
    UP = -1          # Notas suben (FNF clásico)
    DOWN = 1       # Notas bajan (DDR style)

class NoteSurfaces(TypedDict):
    missed: Surface
    default: Surface
    spawned: Surface
    pressed: list[Surface]
    hold: Surface
    end_hold: Surface

class NoteData(TypedDict):
    surfaces: NoteSurfaces
    particles: list[Surface]

NoteDataType = dict["NoteDirection", NoteData]  # Diccionario de charts por nombre


# (!) EN UN FUTURO:
"""
class HitResult(Enum):
    Resultado del input respecto a la nota
    
    NONE = auto()   # No hubo interacción relevante
    HIT = auto()    # Input válido / nota acertada
    MISS = auto()   # Input inválido / nota fallada

class Judgement(Enum):
    PERFECT = auto()
    GOOD = auto()
    BAD = auto()
    MISS = auto()
"""