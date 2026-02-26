from dataclasses import dataclass
from enum import Enum

class DifficultyName(Enum):
    EASY   = "EASY"
    NORMAL = "NORMAL"
    HARD   = "HARD"

@dataclass
class Record:
    """
    Representa un run completado de una dificultad.

    Attributes:
        points:    Puntaje total obtenido.
        perfects:  Notas con timing perfecto.
        goods:     Notas con timing aceptable.
        bads:      Notas con timing malo.
        misses:    Notas no golpeadas.
        max_combo: Combo más largo alcanzado.
        stars:     Estrellas obtenidas (0–4).
        accuracy:  Porcentaje de precisión (0.0–100.0).
        date:      Fecha del run en formato ISO.
    """
    points:    int
    perfects:  int
    goods:     int
    bads:      int
    misses:    int
    max_combo: int
    stars:     int
    accuracy:  float
    date:      str


@dataclass
class Difficulty:
    """
    Representa una dificultad de una canción.

    Attributes:
        name:    Nombre de la dificultad.
        locked:  True si está bloqueada.
        records: Top 3 runs ordenados por (stars DESC, points DESC).
    """
    name:    DifficultyName
    records: list[Record]

    @property
    def stars(self) -> int:
        """Estrellas de la dificultad = stars del record top 1. 0 si no hay records."""
        return self.records[0].stars if self.records else 0

    @property
    def top_record(self) -> Record | None:
        """Retorna el mejor record o None si no hay ninguno."""
        return self.records[0] if self.records else None


@dataclass
class Song:
    """
    Representa una canción con sus 3 dificultades.

    Attributes:
        id:           Índice de la canción (0-based).
        name:         Nombre de la canción. Coincide con la carpeta en assets/songs.
        locked:       True si la canción está bloqueada.
        difficulties: Dificultades indexadas por DifficultyName.
    """
    id:           int
    name:         str
    difficulties: dict[DifficultyName, Difficulty]

    def get_difficulty(self, name: DifficultyName) -> Difficulty | None:
        """Retorna una dificultad por nombre o None si no existe."""
        return self.difficulties.get(name)