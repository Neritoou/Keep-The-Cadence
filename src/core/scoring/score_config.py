from ..types import Judgement

BASE_POINTS: dict[Judgement, int] = {
    Judgement.PERFECT: 350,
    Judgement.GOOD: 200,
    Judgement.BAD: 100,
    Judgement.MISS: 0,
}

# Juicios que cuentan como "acierto" para el combo
HIT_JUDGEMENTS: set[Judgement] = {
    Judgement.PERFECT,
    Judgement.GOOD,
}

# Multiplicador de combo
COMBO_THRESHOLDS: list[tuple[int, float]] = [
    (0, 1.0),       # sin combo
    (5, 1.05),      # 5+ aciertos: x1.05
    (10, 1.1),      # 10+ aciertos: x1.1
    (25, 1.25),     # 25+ aciertos: x1.25
    (50, 1.5),      # 50+ aciertos: x1.5
    (100, 2.0),     # 100+ aciertos: x2.0
]

HOLD_BONUS_FACTOR: float = 0.5

MAX_STARS = 4

# Rangos finales
STARS: list[tuple[float, int]] = [
    (0.0, 1),
    (0.25, 2),
    (0.50, 3),
    (0.75, 4)
]

# Para la barra de rendimiento
PERFORMANCE_DELTA: dict[Judgement, float] = {
    Judgement.PERFECT: +5.0,
    Judgement.GOOD:    +3.0,
    Judgement.BAD:     +0.0,
    Judgement.MISS:    -8.0,
}

PERFORMANCE_ZONES: list[tuple[float, int]] = [
    (0.0, 3),  # muy preocupada
    (0.25, 2),   # preocupada
    (0.45, 0),  # neutral
    (0.75, 1)   # feliz
]

ACCURACY_WEIGHTS = {
    Judgement.PERFECT: 1.0,
    Judgement.GOOD:    0.75,
    Judgement.BAD:     0.5,
}