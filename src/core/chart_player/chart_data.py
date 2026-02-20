from dataclasses import dataclass

from ..note import Note

@dataclass
class ChartSection:
    """Representa una sección del chart ya cargada."""
    index: int
    start_time: float
    end_time: float
    notes: list[Note]

    def __lt__(self, other: "ChartSection"):
        return self.index < other.index

    def get_active_notes(self, current_time: float, spawn_time_ms: float) -> list[Note]:
        """Devuelve las notas visibles en el tiempo actual."""
        return [
            note for note in self.notes
            if note.is_visible(current_time, spawn_time_ms)
        ]

@dataclass
class LoadedChart:
    """Representa un chart completamente cargado."""
    song_name: str
    bpm: float
    pixels_per_ms: float
    sections: list[ChartSection]
    total_duration: float
    total_notes: int
    
    def get_section_at_time(self, current_time: float) -> ChartSection | None:
        """Encuentra la sección activa en un tiempo dado."""
        for section in self.sections:
            if section.start_time <= current_time < section.end_time:
                return section
        return None
    
    def get_all_active_notes(self, current_time: float, spawn_time_ms: float) -> list[Note]:
        """Obtiene todas las notas visibles en el tiempo actual."""
        section = self.get_section_at_time(current_time)

        if section:
            return section.get_active_notes(current_time, spawn_time_ms)
        return []