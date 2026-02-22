from dataclasses import dataclass

@dataclass
class EditorKeyState:
    """
    Estado de una tecla en el editor de charts.
    Trackea si está siendo presionada para crear una nota.
    """
    is_pressed: bool = False        # Si la tecla está presionada
    is_hold_note: bool = False      # Si se convertirá en hold note
    press_start_time: float = 0.0   # Tiempo cuando se presionó
    
    def reset(self) -> None:
        """Reinicia el estado"""
        self.is_pressed = False
        self.is_hold_note = False
        self.press_start_time = 0.0

@dataclass
class EditorInfo:
    """Información del estado del editor"""
    bpm: float
    current_time: float
    song_duration: float
    section_index: int
    total_sections: int
    section_status: str
    notes_count: int
    music_playing: bool
    snap_enabled: bool
    loop_enabled: bool
    can_export: bool
    pixels_per_ms: float