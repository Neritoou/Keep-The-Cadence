# --- TIMING ---
SPAWN_TIME_MS: float = 2000          # Cuánto antes spawna la nota (ms)
INPUT_OFFSET_MS: float = -15.0       # Compensación de input del jugador (ms)
HOLD_END_WINDOW_MS: float = 160.0    # Ventana para soltar hold notes (ms)
MIN_HOLD_DURATION_MS: int = 500      # Duración mínima válida de hold note (ms)
MISS_DISPLAY: float = 0.25           # Tiempo que se muestra el miss (segundos)


# --- ANIMACIÓN ---
MAX_DT_PER_UPDATE_ANIMATION: float = 0.1  # Delta máximo para actualizar animaciones (s)


# --- PUNTUACIÓN ---
MAX_RECORDS: int = 3                 # Máximo de récords guardados por canción


# --- HIT LINE ---
HIT_LINE_Y_UP: int = 70              # Y de la hit line (scroll hacia arriba)
HIT_LINE_Y_DOWN: int = 600           # Y de la hit line (scroll hacia abajo)


# --- COLUMNAS DE NOTAS (X) ---
HIT_LINE_XS: tuple[int, ...] = (680, 820, 960, 1100)           # Juego
HIT_LINE_XS_EDITOR: tuple[int, ...] = (450, 570, 690, 810)     # Editor


# --- PERSONAJE ---
MIKU_PLAY_POSITION: tuple[int, int] = (300, 390)


# --- NOTAS ---
BASE_PIXELS_PER_MS: float = 0.45     # Velocidad base de scroll (px/ms)
NOTE_SIZE_MULTIPLIER: float = 0.6    # Escala de las notas
NOTE_SIZE: tuple[int, int] = (229, 228)


# --- PARTÍCULAS ---
PARTICLE_SPLASH_SIZE: tuple[int, int] = (275, 303)
PARTICLE_SPLASH_PADDING: tuple[int, int] = (10, 10)


# --- UI / ICONOS ---
PERFORMANCE_ICON_SIZE: tuple[int, int] = (600, 380)
MENU_ICON_SIZE: tuple[int, int] = (71, 65)
STARS_ICON_SIZE: tuple[int, int] = (56, 62)
STANDARD_PADDING: tuple[int, int] = (5, 5)


# --- CHARACTER ---
MIKU_SIZE_MULTIPLIER: float = 0.9

MIKU_ANIMATIONS_FILES: dict[str, str] = {
    "IDLE":            "miku_idle.png",
    "HEY":             "miku_hey.png",
    "DIRECTIONS":      "miku_directions.png",
    "MISS_DIRECTIONS": "miku_miss_directions.png",
    "WIN":             "miku_win.png",
}

MIKU_ANIMATIONS: dict[str, dict] = {
    "IDLE":            {"width": 466, "height": 670, "padding_x": 5, "padding_y": 5},
    "HEY":             {"width": 475, "height": 673, "padding_x": 5, "padding_y": 5},
    "DIRECTIONS":      {"width": 485, "height": 699, "padding_x": 5, "padding_y": 5},
    "MISS_DIRECTIONS": {"width": 493, "height": 700, "padding_x": 5, "padding_y": 5},
    "WIN":             {"width": 632, "height": 719, "padding_x": 5, "padding_y": 5},
}
