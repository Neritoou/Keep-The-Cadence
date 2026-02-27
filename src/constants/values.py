BASE_PIXELS_PER_MS = 0.45
SPAWN_TIME_MS = 2000
MAX_DT_PER_UPDATE_ANIMATION = 0.1
MIN_HOLD_DURATION_MS = 500  # Duración mínima en ms que consideras válida
MISS_DISPLAY = 0.25 # EN SEGUNDOS

# DATOS DE LAS NOTAS 
NOTE_SIZE_MULTIPLIER = 0.6
HIT_LINE_Y_UP = 70
HIT_LINE_Y_DOWN = 600
HIT_LINE_XS: tuple[int, ...] = (680, 820, 960, 1100)
HIT_LINE_XS_EDITOR: tuple[int, ...] = (450, 570, 690, 810)

PARTICLE_SPLASH_SIZE = (275, 303)
PARTICLE_SPLASH_PADDING = (10, 10)

NOTE_SIZE = (229, 228)
PERFORMANCE_ICON_SIZE = (600, 380)
MENU_ICON_SIZE = (71, 65)
STARS_ICON_SIZE = (56,62)

STANDARD_PADDING = (5, 5)


HOLD_END_WINDOW_MS: float = 160.0

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
    "WIN": {
        "width": 632,
        "height": 719,
        "padding_x": 5,
        "padding_y": 5
    }
}

MIKU_ANIMATIONS_FILES = {
    "IDLE": "miku_idle.png",
    "HEY": "miku_hey.png",
    "DIRECTIONS": "miku_directions.png",
    "MISS_DIRECTIONS": "miku_miss_directions.png",
    "WIN": "miku_win.png"
}

MIKU_SIZE_MULTIPLIER = 0.9
MIKU_PLAY_POSITION = (300,390)

MAX_RECORDS = 3
