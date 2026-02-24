from ..types import Judgement
from .score_config import BASE_POINTS, PERFORMANCE_DELTA, HOLD_BONUS_FACTOR, COMBO_THRESHOLDS, STARS, HIT_JUDGEMENTS

class ScoreManager:
    """
    Maneja la puntuación, combo, rendimiento y rango durante una partida.
    Recibe los juicios de cada nota y actualiza el estado interno.
    """
    def __init__(self, total_notes: int):
        """
        Args:
            total_notes: Total de notas del chart.
        """
        self._score: int = 0

        self._combo: int = 0           # aciertos consecutivos
        self._max_combo: int = 0       # el combo más alto alcanzado

        self._judgement_counts: dict[Judgement, int] = {j: 0 for j in Judgement}
        
        self._max_possible_score: int = total_notes * BASE_POINTS[Judgement.PERFECT]

        # Para la barra de rendimiento
        self._performance: float = 50.0     # empieza a la mitad, rango 0-100

    def register_tap(self, judgement: Judgement) -> int:
        """
        Registra el resultado de golpear una nota normal (tap).
        
        Args:
            judgement: Juicio de la nota actual (si el toque fue perfecto,
                        bueno, malo o fallo).

        Returns:
            Los puntos ganados en esta nota.
        """
        self._judgement_counts[judgement] += 1
        self._update_performance(judgement)
    
        if judgement not in HIT_JUDGEMENTS:
            self._combo = 0
            return 0
    
        self._combo += 1
        self._max_combo = max(self._max_combo, self._combo)
    
        points = BASE_POINTS[judgement]
        multiplier = self._get_combo_multiplier()
        gained = int(points * multiplier)
    
        self._score += gained

        return gained
    
    def register_hold_release(self, held_ratio: float) -> int:
        """
        Registra el resultado de una nota sostenida (hold note) al soltarla.
        
        El juicio base ya lo procesa register_tap cuando se presiona, esta
        función solo calcula los puntos extra por cuánto se mantuvo.
        
        Args:
            held_ratio: porcentaje de la duración en el que
                        se mantuvo la nota (0.0 - 1.0).
        
        Returns
            Los puntos ganados.
        """
        base = BASE_POINTS[Judgement.PERFECT]
        bonus = int(base * held_ratio * HOLD_BONUS_FACTOR)

        self._score += bonus

        return bonus
    
    def get_stars(self) -> int:
        """Retorna la cantidad de estrellas que se obtuvo en la canción."""
        if self._max_possible_score == 0:
            return STARS[0][1]
        
        ratio = self._score / self._max_possible_score
        stars = STARS[0][1] # En caso de que no entre en el if del for
        
        for min_ratio, name in STARS:
            if ratio >= min_ratio:
                stars = name
        
        return stars
    
    def get_summary(self) -> dict:
        """Devuelve todos los valores (puntuación, estrellas, mayor combo, juicios contados)."""
        return {
            "score":      self._score,
            "stars":       self.get_stars(),
            "max_combo":  self._max_combo,
            "judgements": self.judgement_counts,
        }
    


    # --- HELPERS ---
    def _get_combo_multiplier(self) -> float:
        multiplier = 1.0
        
        for threshold, value in COMBO_THRESHOLDS:
            if self._combo >= threshold:
                multiplier = value
        return multiplier
    
    def _update_performance(self, judgement: Judgement) -> None:
        delta = PERFORMANCE_DELTA.get(judgement, 0.0)
        self._performance = max(0.0, min(100.0, self._performance + delta))



    # --- PROPIEDADES ---
    @property
    def score(self) -> int:
        return self._score

    @property
    def combo(self) -> int:
        return self._combo

    @property
    def max_combo(self) -> int:
        return self._max_combo

    @property
    def performance(self) -> float:
        return self._performance
    
    @property
    def performance_ratio(self) -> float:
        return self._performance / 100.0

    @property
    def judgement_counts(self) -> dict[Judgement, int]:
        return dict(self._judgement_counts)