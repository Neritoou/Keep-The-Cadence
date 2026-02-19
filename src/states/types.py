from enum import Enum, auto

class StateID(Enum):
    MENU = auto()
    PLAY = auto()
    PAUSE = auto()
    CHART_CREATOR = auto()
    CHART_SETUP = auto()
    # Más estados

# ENUM DE OVERLAYS PARA LOS ESTADOS DEL JUEGO
class OverlayType(Enum):
    """Tipo de overlay para estados del juego"""
    NONE = auto()               # Estado principal (sin overlay)
    SEMITRANSPARENT = auto()    # Overlay semi-transparente (muestra fondo)
    FULLSCREEN = auto()         # Overlay completo (oculta fondo)