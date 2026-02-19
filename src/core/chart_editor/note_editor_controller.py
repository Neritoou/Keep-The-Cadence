from typing import TYPE_CHECKING
from ..note import Note
from ..types import NoteDirection
from ...constants import MIN_HOLD_DURATION_MS

if TYPE_CHECKING:
    from .types import Section

class NoteEditorController:
    """Controlador de notas para el editor"""
    def __init__(self, song_duration: int, ms_per_step: float) -> None:
        self.song_duration = song_duration
        self.ms_per_step = ms_per_step
        self.snap_enabled = True

    def snap_time_to_grid(self, time: float) -> float:
        """Ajusta un tiempo al grid más cercano"""
        if not self.snap_enabled:
            return time
        return round(time / self.ms_per_step) * self.ms_per_step
    
    def toggle_snap(self) -> None:
        """Alterna snap to grid"""
        self.snap_enabled = not self.snap_enabled

    def place_note(self, section: "Section", direction: NoteDirection, hit_time: float, duration: float) -> Note:
        """Crea una nota en la sección."""
        hit_time = self.snap_time_to_grid(hit_time)
                
        hit_time = max(hit_time, section.start_time) # Asegurar que esté dentro de la Sección
        hit_time = min(hit_time, self.song_duration - self.ms_per_step) # Evitar que supere la sección

        # Validar duración mínima ANTES del snap
        if duration < MIN_HOLD_DURATION_MS: 
            duration = 0.0
        else:
            # Limitar duración por canción
            max_song_duration = self.song_duration - hit_time
            duration = min(duration, max_song_duration)

            # No salir de la sección
            if section.end_time is not None:
                duration = min(duration, section.end_time - hit_time)

        duration = self.snap_time_to_grid(duration)
        duration = max(duration, 0.0)
                     
        # Crear y agregar 
        note = Note(hit_time = int(round(hit_time)), duration = int(round(duration)), direction = direction)
        section.notes.append(note)
        section.notes.sort(key=lambda n: n.hit_time)

        return note
    
    def can_remove_last_note(self, section: "Section") -> bool:
        """Verifica si se puede eliminar la última nota"""
        return section.end_time is None and bool(section.notes)
    
    def remove_last_note(self, section: "Section") -> Note:
        """Elimina la última nota colocada en una sección"""
        return section.notes.pop()