from ..core.types import Judgement

BASE_PIXELS_PER_MS = 0.45
SPAWN_TIME_MS = 2000
MAX_DT_PER_UPDATE_ANIMATION = 0.1
MIN_HOLD_DURATION_MS = 500  # Duración mínima en ms que consideras válida
MISS_DISPLAY = 0.25 # EN SEGUNDOS

# DATOS DE LAS NOTAS 
NOTE_SIZE_MULTIPLIER = 0.6
HIT_LINE_Y_UP = 70
HIT_LINE_Y_DOWN = 600
HIT_LINE_XS: tuple[int,int,int,int] = (400, 550, 700, 850) # Cambiar
HIT_LINE_XS_EDITOR: tuple[int,int,int,int] = (450, 570, 690, 810)

PARTICLE_SPLASH_SIZE = (275, 303)
PARTICLE_SPLASH_PADDING = (10, 10)

NOTE_SIZE = (229, 228)
PERFORMANCE_ICON_SIZE = (600, 380)
MENU_ICON_SIZE = (71, 65)

STANDARD_PADDING = (5, 5)


JUDGEMENT_WINDOWS: list[tuple[float, Judgement]] = [
    (45,  Judgement.PERFECT),
    (90,  Judgement.GOOD),
    (135, Judgement.BAD),
]

# Ventana total de hit en ms (±135ms alrededor del hit_time)
HIT_WINDOW_MS: float = 135.0
HOLD_END_WINDOW_MS: float = 100.0

SCROLL_SPEEDS = {
    "EASY": 0.75,
    "NORMAL": 1.0,
    "HARD": 1.5
}

# DATOS DE SPRITESHEET MIKU
MIKU_ANIMATIONS = {
    "IDLE": {
        "width": 466,
        "height": 670,
        "padding_x": 5,
        "padding_y": 5,
    },
    "HEY": {
        "width": 475,
        "height": 673,
        "padding_x": 5,
        "padding_y": 5,
    },
    "DIRECTIONS": {
        "width": 485,
        "height": 699,
        "padding_x": 5,
        "padding_y": 5,
    },
    "MISS_DIRECTIONS": {
        "width": 493,
        "height": 700,
        "padding_x": 5,
        "padding_y": 5,
    },
}

MIKU_ANIMATIONS_FILES = {
    "IDLE": "miku_idle.png",
    "HEY": "miku_hey.png",
    "DIRECTIONS": "miku_directions.png",
    "MISS_DIRECTIONS": "miku_miss_directions.png",
}

MAX_RECORDS = 3
