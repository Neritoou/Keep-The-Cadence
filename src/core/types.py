from enum import Enum, IntEnum
from typing import TypedDict

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
    UP = 1          # Notas suben (FNF clásico)
    DOWN = -1       # Notas bajan (DDR style)

class NoteData(TypedDict):
    """Representación JSON de una nota"""
    hitTime: float      # Tiempo cuando debe golpearse (ms)
    duration: float     # Duración de hold note (0 si es TAP)
    direction: int      # Dirección (0=LEFT, 1=DOWN, 2=UP, 3=RIGHT)

class SectionData(TypedDict):
    """Representación JSON de una sección"""
    index: int          # Índice de la sección
    startTime: float    # Tiempo de inicio (ms)
    endTime: float      # Tiempo de fin (ms)
    notes: list[NoteData]  # Lista de notas en la sección

class ChartData(TypedDict):
    """Representación JSON completa del chart"""
    song: str               # Path al archivo de audio
    bpm: int                # BPM de la canción
    pixels_per_ms: float            # Velocidad de scroll
    sections: list[SectionData]  # Lista de secciones
