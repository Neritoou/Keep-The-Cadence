from dataclasses import dataclass
from .types import Judgement


@dataclass(frozen=True)
class DifficultyData:
    """
    Agrupa todos los valores que cambian según la dificultad.
    Se crea una vez en PlayState y se pasa a ChartPlayer.
    NoteInputHandler la lee via player.config.
    """
    # --- Ventanas de hit ---
    hit_window_ms:      float
    judgement_windows:  tuple[tuple[float, Judgement], ...]

    # --- Velocidad visual ---
    pixels_per_ms_mult: float

    # --- Puntuación ---
    points_multiplier:  float

    # --- Performance ---
    miss_performance:   float   # delta negativo al fallar una nota


DIFFICULTY_DATA: dict[str, DifficultyData] = {
    "EASY": DifficultyData(
        hit_window_ms      = 175.0,
        judgement_windows  = (
            (65,  Judgement.PERFECT),
            (120, Judgement.GOOD),
            (175, Judgement.BAD),
        ),
        pixels_per_ms_mult = 0.75,
        points_multiplier  = 0.8,
        miss_performance   = -5.0,
    ),
    "NORMAL": DifficultyData(
        hit_window_ms      = 135.0,
        judgement_windows  = (
            (45,  Judgement.PERFECT),
            (90,  Judgement.GOOD),
            (135, Judgement.BAD),
        ),
        pixels_per_ms_mult = 1.0,
        points_multiplier  = 1.0,
        miss_performance   = -8.0,
    ),
    "HARD": DifficultyData(
        hit_window_ms      = 95.0,
        judgement_windows  = (
            (30,  Judgement.PERFECT),
            (65,  Judgement.GOOD),
            (95,  Judgement.BAD),
        ),
        pixels_per_ms_mult = 1.3,
        points_multiplier  = 1.3,
        miss_performance   = -12.0,
    ),
}