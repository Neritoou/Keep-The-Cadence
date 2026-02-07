class Note:
    """Representa una nota individual en el juego y el editor."""
    def __init__(self, hit_time: float, duration: float, direction: int):
        """
        asd

        Args:
            hit_time: Tiempo en ms cuando debe ser golpeada
            duration: Duración en ms (para notas largas, 0 si no es larga)
            direction: 0: up, 1: down, 2: left, 3: right
        """
        self.hit_time = hit_time
        self.direction = direction
        self.duration = duration 

    @property
    def end_time(self) -> float:
        """Tiempo cuando termina una hold note"""
        return self.hit_time + self.duration
        
    @property
    def is_hold_note(self) -> bool:
        """¿Es una nota larga?"""
        return self.duration > 0
    
    def is_visible(self, current_time: float, spawn_time_ms: float) -> bool:
        return (self.hit_time - spawn_time_ms <= current_time <= self.end_time)

    def is_hittable(self, current_time: float, hit_window: float = 180) -> bool:
        """
        Verifica si la nota puede ser golpeada en el tiempo actual.
        
        Args:
            current_time: Tiempo actual (ms)
            hit_window: Ventana de tiempo válida (ms)
            
        Returns:
            True si puede ser golpeada
        """
        time_diff = abs(self.hit_time - current_time)
        return time_diff <= hit_window
    
    def get_hit_accuracy(self, hit_time: float) -> tuple[str, int]:
        """
        Calcula la precisión de un golpe.
        
        Args:
            hit_time: Tiempo cuando el jugador golpeó (ms)
            
        Returns:
            Tupla de (rating, puntos)
        """
        time_diff = abs(self.hit_time - hit_time)
        
        if time_diff <= 45:
            return ("perfect", 350)
        elif time_diff <= 90:
            return ("good", 200)
        elif time_diff <= 135:
            return ("bad", 100)
        elif time_diff <= 180:
            return ("shit", 50)
        else:
            return ("miss", 0)