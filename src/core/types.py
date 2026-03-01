from enum import Enum, IntEnum, auto
from pygame import Surface
from typing import TypedDict, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .note import Note

@dataclass
class Section:
    """Representa una sección del chart"""
    index: int
    start_time: float  # ms
    end_time: float # ms, 0.0 si está abierta
    notes: "list[Note]"

    def __lt__(self, other: "Section"):
        return self.index < other.index

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
    pixels_per_ms: float    # Velocidad de scroll
    song_duration: float    # Duración en MS de la canción
    total_notes: int        # Cantidad de notas en toda la canción
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
    UP = -1        # Notas suben (FNF clásico)
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

class Judgement(Enum):
    PERFECT = auto()  # ±45ms
    GOOD    = auto()  # ±90ms
    BAD     = auto()  # ±135ms
    MISS    = auto()  # nota no tocada

class NoteState(Enum):
    PENDING   = auto() 
    ACTIVE    = auto() 
    COMPLETED = auto() 
    MISSED    = auto() 

@dataclass
class ChartData:
    """Representa los datos JSON del Chart pero en un dataclass"""
    song_name: str
    bpm: float
    pixels_per_ms: float
    song_duration: float
    total_notes: int
    sections: "list[Section]"
    _section_index: int = 0

    @property
    def current_section(self) -> Section:
        return self.sections[self._section_index]
    
    def advance_section(self, current_time: float) -> None:
        """Avanza el índice si la sección actual ya terminó."""
        if current_time < self.sections[self._section_index].end_time:
            return
        
        if self._section_index < len(self.sections) - 1:
            self._section_index += 1
    
    def get_current_notes(self, current_time: float, spawn_time_ms: float) -> "list[Note]":
        """Retorna las notas activas de la sección actual + siguiente (si existe)."""
        result: list[Note] = []

        sections = [self.current_section]
        next_index = self._section_index + 1
        if next_index < len(self.sections):
            sections.append(self.sections[next_index])

        for section in sections:
            for note in section.notes:
                # Las notas están ordenadas por hit_time.
                # Si esta no ha spawneado, las siguientes tampoco → salir.
                if note.hit_time - spawn_time_ms > current_time:
                    break
                if note.is_active(current_time, spawn_time_ms):
                    result.append(note)

        return result

    def reset(self) -> None:
        for section in self.sections[:self._section_index + 2]:
            for note in section.notes:
                if note.state != NoteState.PENDING:
                    note.reset()
        self._section_index = 0