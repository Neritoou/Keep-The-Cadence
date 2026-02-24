from typing import TYPE_CHECKING
from .types import Judgement
from ..constants import HIT_WINDOW_MS, JUDGEMENT_WINDOWS
from enum import Enum, auto

if TYPE_CHECKING:
    from .types import NoteDirection

class NoteState(Enum):
    PENDING   = auto() 
    ACTIVE    = auto() 
    COMPLETED = auto() 
    MISSED    = auto() 
    
class Note:
    def __init__(self, hit_time: float, duration: float, direction: "NoteDirection"):
        self.hit_time  = hit_time
        self.direction = direction
        self.duration  = duration
        self.state     = NoteState.PENDING

    def __lt__(self, other: "Note") -> bool:
        return self.hit_time < other.hit_time

    # --- PROPIEDADES DE ESTADO ---

    @property
    def is_resolved(self) -> bool:
        """Devuelve Verdadero si la notá fue completada o fallada."""
        return self.state in (NoteState.COMPLETED, NoteState.MISSED)

    @property
    def was_hit(self) -> bool:
        """La cabeza fue golpeada exitosamente. Útil para Score: 
        una hold dropeada (MISSED) pudo haber sido golpeada primero."""
        return self.state in (NoteState.ACTIVE, NoteState.COMPLETED)

    @property
    def end_time(self) -> float:
        return self.hit_time + self.duration

    @property
    def is_hold_note(self) -> bool:
        return self.duration > 0

    # --- TRANSICIONES ---

    def on_hit(self) -> None:
        self.state = NoteState.ACTIVE if self.is_hold_note else NoteState.COMPLETED

    def on_completed(self) -> None:
        self.state = NoteState.COMPLETED

    def on_missed(self) -> None:
        self.state = NoteState.MISSED

    # --- VISIBILIDAD Y ACTIVIDAD ---

    def is_visible(self, current_time: float, spawn_time_ms: float) -> bool:
        """Rango visual: desde que spawna hasta que termina."""
        return self.hit_time - spawn_time_ms <= current_time <= self.end_time

    def is_active(self, current_time: float, spawn_time_ms: float) -> bool:
        """Si la nota aún debe procesarse¿?"""
        if current_time < self.hit_time - spawn_time_ms:
            return False

        if self.state == NoteState.COMPLETED:
            return False

        if self.state == NoteState.MISSED:
            # Hold perdida: sigue visible hasta end_time
            # Tap perdida: ya fue procesada por pop_missed_notes, fuera
            return self.is_hold_note and current_time <= self.end_time

        if self.state == NoteState.ACTIVE:
            return current_time <= self.end_time

        return True  # PENDING: permanece hasta ser resuelta

    def is_hittable(self, current_time: float) -> bool:
        """Devuelve verdadero si la nota debe procesar Input"""
        return abs(self.hit_time - current_time) <= HIT_WINDOW_MS

    def is_missed(self, current_time: float) -> bool:
        """Ventana expirada sin que fuera tocada (solo PENDING)."""
        return self.state == NoteState.PENDING and current_time >= self.hit_time + HIT_WINDOW_MS

    # --- JUICIO ---
    def get_judgement(self, current_time: float) -> Judgement:
        diff = abs(self.hit_time - current_time)
        for window, judgement in JUDGEMENT_WINDOWS:
            if diff <= window:
                return judgement
        return Judgement.MISS