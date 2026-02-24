import pygame
from typing import TYPE_CHECKING

from ...ui import UIElement
from ...core.scoring import PERFORMANCE_ZONES

if TYPE_CHECKING:
    from ...resources import SpriteSheet
    from ...ui import ColorValue

class PerformanceBar(UIElement):
    """
    Barra de rendimiento visual que muestra el estado de rendimiento del jugador.

    El ícono elegido se desliza suavemente a lo largo de la barra y cambia de
    aspecto según la zona en la que se encuentre.
    """

    # Colores de las zonas de la barra
    ZONE_COLORS: list[tuple[float, "ColorValue"]] = [
        (0.0, (172, 5, 5)),         # rojo oscuro
        (0.25, (255, 0, 0)),        # rojo
        (0.45, (180, 180, 180)),    # gris neutro
        (0.55, (80, 180, 100)),     # verde
        (0.75, (0,  100, 0)),       # verde mas oscuro
    ]

    def __init__(
        self, name: str, x: int, y: int, width: int,
        icon_spritesheet: "SpriteSheet", 
        icon_display_size: tuple[int, int] = (90, 75),
        icon_lerp_speed: float = 2.0, bar_height: int = 16
    ):
        """
        Args:
            x, y: Posición de la barra (esquina superior izquierda).
            width: Ancho total de la barra.
            icon_spritesheet: Spritesheet con los diferentes aspectos.
            icon_display_size: Tamaño al que se escala el ícono en pantalla.
            bar_height: Alto de la barra en píxeles.
        """
        super().__init__(name, x, y, width, bar_height, visible=True)

        self._bar_width  = width
        self._bar_height = bar_height
        self._icon_size  = icon_display_size
        self._icon_lerp = icon_lerp_speed

        # Posición visual actual del ícono (0.0 - 1.0), se interpola
        self._display_ratio: float = 0.5

        # Valor objetivo (del ScoreManager)
        self._target_ratio:  float = 0.5

        # Carga los 4 frames del ícono
        self._icon_frames: list[pygame.Surface] = [
            pygame.transform.smoothscale(
                icon_spritesheet.get_frame_at(0, col, trim=True),
                icon_display_size
            )
            for col in range(4)
        ]

        # Índice del frame actualmente visible
        self._current_frame_index: int = self._get_frame_index(self._display_ratio)

        # Superficies de la barra
        self._bar_surface = pygame.Surface((width, bar_height), pygame.SRCALPHA)
        self._bar_bg_surface = pygame.Surface((width, bar_height), pygame.SRCALPHA)
        self._rebuild_bg()

    def set_performance(self, performance_ratio: float) -> None:
        """
        Actualiza el valor objetivo de la barra.

        Args:
            performance_ratio: Valor normalizado entre 0.0 y 1.0
        """
        self._target_ratio = max(0.0, min(1.0, performance_ratio))

    def update(self, dt: float) -> None:
        super().update(dt)

        # Interpola suavemente hacia el objetivo
        diff = self._target_ratio - self._display_ratio
        self._display_ratio += diff * self._icon_lerp * dt

        # Actualizar frame del ícono según zona
        self._current_frame_index = self._get_frame_index(self._display_ratio)

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        bx, by = self.rect.topleft

        surface.blit(self._bar_bg_surface, (bx, by))

        # Relleno de la barra según valor actual
        fill_w = int(self._bar_width * self._display_ratio)

        if fill_w > 0:
            fill_color = self._get_zone_color(self._display_ratio)
            fill_rect  = pygame.Rect(bx, by, fill_w, self._bar_height)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=6)

        # Borde de la barra
        pygame.draw.rect(
            surface, (255, 255, 255),
            pygame.Rect(bx, by, self._bar_width, self._bar_height),
            width=2, border_radius=6
        )

        # Líneas
        mid_x = bx + self._bar_width // 2
        pygame.draw.line(
            surface, (255, 255, 255, 160),
            (mid_x, by), (mid_x, by + self._bar_height - 1), 2
        )

        quarter_x = self._bar_width // 4
        pygame.draw.line(
            surface, (255, 255, 255, 160),
            (bx + quarter_x, by), (bx + quarter_x, by + self._bar_height - 1), 2
        )

        third_quarter_x = bx + quarter_x * 3
        pygame.draw.line(
            surface, (255, 255, 255, 160),
            (third_quarter_x, by), (third_quarter_x, by + self._bar_height - 1), 2
        )

        # Ícono centrado verticalmente sobre su posición en la barra
        icon = self._icon_frames[self._current_frame_index]
        icon_x = bx + int(self._display_ratio * self._bar_width) - self._icon_size[0] // 2
        icon_y = by + self._bar_height // 2 - self._icon_size[1] // 2
        surface.blit(icon, (icon_x, icon_y))



    # --- HELPERS PRIVADOS ---
    def _get_frame_index(self, ratio: float) -> int:
        """Retorna el índice de columna del spritesheet según la zona."""
        index = PERFORMANCE_ZONES[0][1]

        for min_ratio, col in PERFORMANCE_ZONES:
            if ratio >= min_ratio:
                index = col
        
        return index

    def _get_zone_color(self, ratio: float) -> "ColorValue":
        """Retorna el color de relleno según la zona actual."""
        color = self.ZONE_COLORS[0][1]

        for min_ratio, c in self.ZONE_COLORS:
            if ratio >= min_ratio:
                color = c
        return color

    def _rebuild_bg(self) -> None:
        """Construye el fondo oscuro semitransparente de la barra."""
        self._bar_bg_surface.fill((0, 0, 0, 0))

        pygame.draw.rect(
            self._bar_bg_surface, (30, 30, 30, 180),
            pygame.Rect(0, 0, self._bar_width, self._bar_height),
            border_radius=6
        )