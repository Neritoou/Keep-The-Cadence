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
    judgement_windows:  tuple[tuple[float, Judgement], ...]

    # --- Velocidad visual ---
    pixels_per_ms_mult: float

    # --- Puntuación ---
    points_multiplier:  float

    # --- Performance ---
    miss_performance:   float   # delta negativo al fallar una nota

    @property
    def hit_window_ms(self) -> float:
        return self.judgement_windows[-1][0]


DIFFICULTY_DATA: dict[str, DifficultyData] = {
    "EASY": DifficultyData(
        judgement_windows  = (
            (80,  Judgement.PERFECT),   # 65  -> 80
            (135, Judgement.GOOD),      # 120 -> 135
            (190, Judgement.BAD),       # 175 -> 190
        ),
        pixels_per_ms_mult = 0.75,
        points_multiplier  = 0.8,
        miss_performance = -3.0,   # -5.0 -> -3.0
    ),
    "NORMAL": DifficultyData(
        judgement_windows  = (
            (60,  Judgement.PERFECT),   # 45  -> 60
            (105, Judgement.GOOD),      # 90  -> 105
            (150, Judgement.BAD),       # 135 -> 150
        ),
        pixels_per_ms_mult = 1.0,
        points_multiplier  = 1.0,
        miss_performance = -5.0,   # -8.0 -> -5.0
    ),
    "HARD": DifficultyData(
        judgement_windows  = (
            (45,  Judgement.PERFECT),   # 30  -> 45
            (80,  Judgement.GOOD),      # 65  -> 80
            (110, Judgement.BAD),       # 95  -> 110
        ),
        pixels_per_ms_mult = 1.3,
        points_multiplier  = 1.3,
        miss_performance = -8.0,   # -12.0 -> -8.0
    ),
}