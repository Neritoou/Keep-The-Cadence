from enum import Enum, auto

class StateID(Enum):
    MENU = auto()
    PLAY = auto()
    PAUSE = auto()
    GAME_OVER = auto()
    WIN = auto()
    OPTIONS = auto()
    CHART_CREATOR = auto()
    CHART_SETUP = auto()
    SONG_SELECT = auto()
    TRANSITION   = auto()
    KEYBIND_EDITOR = auto()
    COUNTDOWN = auto()
    CREDITS = auto()
    # Más estados

# ENUM DE OVERLAYS PARA LOS ESTADOS DEL JUEGO
class OverlayType(Enum):
    """Tipo de overlay para estados del juego"""
    NONE = auto()               # Estado principal (sin overlay)
    SEMITRANSPARENT = auto()    # Overlay semi-transparente (muestra fondo)
    FULLSCREEN = auto()         # Overlay completo (oculta fondo)