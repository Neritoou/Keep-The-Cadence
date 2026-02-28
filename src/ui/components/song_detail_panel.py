import pygame
from typing import Optional, TYPE_CHECKING

from .panel import UIPanel
from .label import UILabel
from ...core.database import Song, DifficultyName, Record

if TYPE_CHECKING:
    from ...ui import ColorValue

class UISongDetailPanel(UIPanel):
    """Panel especializado para mostrar los detalles y récords de una canción."""
    
    # Colores y constantes
    DIFF_COLORS = {
        DifficultyName.EASY:   (100, 220, 110),
        DifficultyName.NORMAL: (100, 185, 255),
        DifficultyName.HARD:   (255, 90,  90),
    }

    RANK_COLORS = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
    DIM = (120, 110, 150)

    def __init__(
            self, name: str, x: int, y: int, width: int, height: int,
            fonts: dict, stars_sprites: list[pygame.Surface],
            bg_color: "ColorValue", border_color: tuple
    ):
        super().__init__(name, x, y, width, height, bg_color, border_color, radius=45)
        
        self.fonts = fonts
        self.stars_sprites = stars_sprites
        
        # Datos actuales
        self.current_song: Optional[Song] = None
        self.current_diff_name: Optional[DifficultyName] = None
        self.records: list[Record] = []
        
        self.cx = x + 40
        self.cy = y + 35

        # Nombre de la canción
        self.song_title_label = UILabel(
            "song_detail_title", self.cx, self.cy, 
            "Seleccione la dificultad...", font=self.fonts['song'], color=(245, 235, 255), center=False
        )

        # Dificultad (para el texto del la pildora)
        self.diff_label = UILabel(
            "song_detail_diff", self.rect.x + self.rect.w // 2, self.cy + 74,
            "...", self.fonts['medium'], (255, 255, 255), center=True
        )

        # Encabezado de Récords
        self.records_header = UILabel(
            "song_detail_records_hdr", x + (width // 2), self.cy + 200, 
            "MEJORES REGISTROS", self.fonts['small'], (170, 140, 255), center=True
        )

        self.rank_header = UILabel(
            "song_rank_header", self.cx, self.cy + 250, 
            "Rango", self.fonts['small'], self.DIM, center=False
        )
        self.points_header = UILabel(
            "song_points_header", self.cx + 260, self.cy + 250, 
            "Puntos", self.fonts['small'], self.DIM, center=False
        )
        self.accuracy_header = UILabel(
            "song_accuracy_header", self.cx + 440, self.cy + 250, 
            "Precisión", self.fonts['small'], self.DIM, center=False
        )

        # Label genérico para cuando no hay récords
        self.no_records_label = UILabel(
            "song_detail_no_records", self.cx, self.cy + 200, 
            "Sin registros todavia...", self.fonts['small'], self.DIM, center=False
        )

    def set_data(self, song: Song, diff_name: DifficultyName, records: list[Record]):
        """Actualiza los datos solo si han cambiado para optimizar el renderizado."""
        if (self.current_diff_name != diff_name or 
            self.records != records):

            self.current_diff_name = diff_name
            self.records = records

            self.diff_label.set_text(diff_name.value)
            self.diff_label.center_at(self.rect.x + self.rect.w // 2)

            color = self.DIFF_COLORS.get(diff_name, (255, 255, 255))
            self.diff_label.set_color(color)

    def _draw_difficulty_selector(self, surface: pygame.Surface):
        """Dibuja solo las geometrías estáticas (rectángulos y líneas) en pantalla."""
        if not self.current_diff_name:
            return

        # Dibuja la Píldora
        color = self.DIFF_COLORS.get(self.current_diff_name, (255, 255, 255))
        px, py = self.rect.x + self.rect.w // 2 - 155, self.cy + 70
        w, h = 310, 48

        bg_color = pygame.Color(color)
        bg_color.a = 45

        bd_color = pygame.Color(color)
        bd_color.a = 210

        pill_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(pill_surf, bg_color, (0, 0, w, h), border_radius=24)
        pygame.draw.rect(pill_surf, bd_color, (0, 0, w, h), width=2, border_radius=24)
        surface.blit(pill_surf, (px, py))

        # Flechas
        arr_color = pygame.Color(*color)
        arr_color.a = 200
        left = self.fonts['medium'].render("<", True, arr_color)
        right = self.fonts['medium'].render(">", True, arr_color)
        surface.blit(left, (px - 20, py + 4))
        surface.blit(right, (px + w + 10, py + 4))

        # Divisor
        div_color = pygame.Color(self.border_color)
        div_color.a = 100
        pygame.draw.line(surface, div_color, (self.cx, py + h + 40), (self.cx + 560, py + h + 40), 2)

    def _draw_dynamic_records(self, surface: pygame.Surface):
        """Dibuja las estrellas y los textos de los récords."""
        if not self.records:
            self.no_records_label.render(surface)
            return

        ry = self.cy + 300

        for rank, rec in enumerate(self.records[:10], 1):
            rank_color = self.RANK_COLORS[rank - 1] if rank <= 3 else self.DIM
            
            rank_surf = self.fonts['small'].render(f"#{rank}", True, rank_color)
            pts_surf = self.fonts['small'].render(f"{rec.points:,} pts", True, (220, 215, 235))
            accuracy_surf = self.fonts['small'].render(f"{rec.accuracy:.1f}%", True, (170, 165, 200))

            surface.blit(rank_surf, (self.cx, ry))
            surface.blit(pts_surf, (self.cx + 260, ry))
            surface.blit(accuracy_surf, (self.cx + 440, ry))

            # Estrellas
            star_w = self.stars_sprites[0].get_width()
            for i in range(4):
                frame = self.stars_sprites[0] if i < rec.stars else self.stars_sprites[1]
                surface.blit(frame, (self.cx + 80 + i * (star_w + 4), ry))
            
            ry += 40

    def update(self, dt: float) -> None:
        super().update(dt)
        self.diff_label.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
            
        # Dibuja el panel de fondo
        super().render(surface)
        
        self._draw_difficulty_selector(surface)
            
        self.song_title_label.render(surface)
        self.diff_label.render(surface)


        if self.records:
            self.records_header.render(surface)
            self.rank_header.render(surface)
            self.points_header.render(surface)
            self.accuracy_header.render(surface)
            self._draw_dynamic_records(surface)
        else:
            self.no_records_label.render(surface)