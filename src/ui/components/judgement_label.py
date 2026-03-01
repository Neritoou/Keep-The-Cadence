import pygame
from typing import TYPE_CHECKING
from .label import UILabel

if TYPE_CHECKING:
    from ...core.types import Judgement

class UIJudgementLabel(UILabel):
    """
    Etiqueta flotante que muestra el juicio de una nota (PERFECT, GOOD, etc.).
    Al aparecer, da un pequeño salto y luego flota hacia arriba mientras hace fade out.
    """
    def __init__(self, name: str, x: int, y: int, font: pygame.font.Font):
        # Iniciamos invisible y con alpha 0
        super().__init__(name, x, y, "", font, (255, 255, 255), center=True, visible=False, alpha=0)
        
        self.base_y = y
        self._exact_y = float(y)
        self.float_speed = 45.0  # Píxeles por segundo que sube

    def show_judgement(self, judgement: "Judgement") -> None:
        """Configura el texto, color y reinicia la animación de aparición."""
        
        judgement_config = {
            "PERFECT": ("PERFECTO!", (0, 255, 255)),   # Cyan brillante
            "GOOD":    ("BIEN", (100, 255, 100)), # Verde claro
            "BAD":     ("MAL", (255, 150, 0)),   # Naranja
            "MISS":    ("FALLO", (255, 50, 50))    # Rojo
        }
        
        text, color = judgement_config.get(judgement.name, (judgement.name, (255, 255, 255)))
        
        self.set_text(text)
        self.set_color(color)
        
        # Reiniciar el estado visual
        self.visible = True
        self.alpha = 255
        
        # Darle un pequeño "salto" hacia abajo inicial para que el movimiento se note más
        self._exact_y = self.base_y + 10.0
        self.rect.y = int(self._exact_y)
        
        # Iniciar el desvanecimiento (fade out en 0.5 segundos)
        self.fade_to(0, 0.5)

    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Efecto de flotar hacia arriba de forma fluida (usando float)
        if self.visible and self.alpha > 0:
            self._exact_y -= self.float_speed * dt
            self.rect.y = int(self._exact_y)
            
        elif self.alpha <= 0:
            self.visible = False