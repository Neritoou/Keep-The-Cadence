import pygame
from pathlib import Path
from .game_state import GameState
from ..states.types import StateID, OverlayType
from ..util.paths import list_song_folders, get_full_song_path, get_chart_path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.game import Game

# (!) HECHO RAPIDAMENTE POR LA IA, CAMBIAR.
class ChartSetupState(GameState):
    """Estado de configuración inicial del editor, permite seleccionar carpeta de canción y chart."""

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.width, self.height = 1280, 720

        self.font_medium = pygame.font.Font(None, 32)
        self.folder_font = pygame.font.Font(None, 32)

        self.title_font = pygame.font.Font(None, 72)
        self.select_color = ((100, 180, 100), (255, 255, 255), (150, 230, 150))
        self.not_select_color = ((50, 50, 50), (200, 200, 200), (80, 80, 80))

        # --- BPM ---
        self.bpm_font = pygame.font.Font(None, 48)


        # --- Título principal ---
        self.title_text = self.title_font.render("CHART EDITOR", True, (255, 215, 0))
        self.title_rect = self.title_text.get_rect(center=(self.width // 2, 60))

        self.bpm: int = 120
        self.selected_index = 0
    
        # Sistema de scroll
        self.visible_count = 7       # máximo de carpetas visibles
        self.scroll_offset = 0       # desde qué índice empezar a dibujar

        self.song_path: str | None = None
        self.chart_path: str | None = None

        # --- Carpeta raíz de canciones ---
        self.songs_root = Path("assets/songs")
        self.song_folders = list_song_folders()
        self.selected_index = 0  # Carpeta actualmente seleccionada

    def on_exit(self) -> None:
        return super().on_exit()
    
    def on_enter(self) -> None:
        return super().on_enter()
    
    def update(self, dt: float) -> None:
        if self._can_start():
            self._start_editor()

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if not self.song_folders:
            return

        # --- Navegación en la lista de carpetas ---
        if self.game.input.is_key_pressed(pygame.K_DOWN):
            self.next_folder()

        elif self.game.input.is_key_pressed(pygame.K_UP):
            self.previous_folder()

        # --- Ajuste de BPM ---
        if self.game.input.is_key_pressed(pygame.K_RIGHT):
            self.bpm += 1
            
        elif self.game.input.is_key_pressed(pygame.K_LEFT):
            self.bpm = max(0, self.bpm-1)

        # --- Seleccionar carpeta y preparar paths ---
        if self.game.input.is_key_pressed(pygame.K_RETURN):
            folder = self.song_folders[self.selected_index]

            # Guardar paths
            self.song_path = str(get_full_song_path(folder))
            self.chart_path = str(get_chart_path(folder))

        # --- Salir del estado ---
        if self.game.input.is_key_pressed(pygame.K_ESCAPE):
            self.game.state.exit_current()

    def _can_start(self) -> bool:
        return self.song_path is not None and self.chart_path is not None and self.bpm > 0

    def _start_editor(self) -> None:
        self.game.state.change(
            StateID.CHART_CREATOR,
            song_path = self.song_path,
            chart_path = self.chart_path,
            song_name = self.song_folders[self.selected_index],
            bpm = self.bpm
        )

    def _update_scroll(self):
        """
        Ajusta el scroll para que la carpeta seleccionada siempre esté visible.
        """
        if len(self.song_folders) <= self.visible_count:
            self.scroll_offset = 0
            return

        # Asegurar que selected_index esté visible
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_count:
            self.scroll_offset = self.selected_index - self.visible_count + 1

    def next_folder(self):
        """Mueve a la siguiente carpeta"""
        self.selected_index = (self.selected_index + 1) % len(self.song_folders)
        self._update_scroll()

    def previous_folder(self):
        """Mueve a la carpeta anterior"""
        self.selected_index = (self.selected_index - 1) % len(self.song_folders)
        self._update_scroll()

    def render(self, surface: pygame.Surface) -> None:
        # Fondo
        surface.fill((30, 30, 30))

        surface.blit(self.title_text, self.title_rect)

        bpm_text = self.bpm_font.render(f"BPM: {self.bpm:.0f}", True, (255, 255, 255))
        bpm_rect = bpm_text.get_rect(center=(self.width // 2, 130))
        surface.blit(bpm_text, bpm_rect)

        # --- Área de carpetas con scroll ---
        folder_area_top = 180
        folder_item_height = 45
        
        # Calcular qué carpetas mostrar
        visible_folders = self.song_folders[
            self.scroll_offset : self.scroll_offset + self.visible_count
        ]

        for i, folder in enumerate(visible_folders):
            actual_index = self.scroll_offset + i
            is_selected = actual_index == self.selected_index

            # Posición vertical
            item_y = folder_area_top + i * folder_item_height

            # Dimensiones del rectángulo
            rect_width = 300
            rect_height = 40
            rect_x = (self.width - rect_width) // 2
            rect_y = item_y
            border_radius = 10  # Radio de las esquinas redondeadas

            colors = self.select_color if is_selected else self.not_select_color

            # Dibujar rectángulo de fondo con bordes redondeados
            pygame.draw.rect(
                surface,
                colors[0],
                (rect_x, rect_y, rect_width, rect_height),
                border_radius=border_radius
            )

            # Dibujar borde
            pygame.draw.rect(
                surface,
                colors[2],
                (rect_x, rect_y, rect_width, rect_height),
                width=2,  # grosor del borde
                border_radius=border_radius
            )

            # Texto centrado
            text_surface = self.folder_font.render(folder, True, colors[1])
            text_rect = text_surface.get_rect(
                center=(self.width // 2, item_y + rect_height // 2)
            )
            surface.blit(text_surface, text_rect)

        # --- Indicador de scroll ---
        if len(self.song_folders) > self.visible_count:
            indicator_font = pygame.font.Font(None, 24)
            
            # Flecha arriba
            if self.scroll_offset > 0:
                up_arrow = indicator_font.render("[UP] Más arriba", True, (150, 150, 150))
                up_rect = up_arrow.get_rect(center=(self.width // 2, folder_area_top - 15))
                surface.blit(up_arrow, up_rect)
            
            # Flecha abajo
            if self.scroll_offset + self.visible_count < len(self.song_folders):
                down_arrow = indicator_font.render("[DOWN] Más abajo", True, (150, 150, 150))
                down_y = folder_area_top + self.visible_count * folder_item_height + 10
                down_rect = down_arrow.get_rect(center=(self.width // 2, down_y))
                surface.blit(down_arrow, down_rect)

            # Contador de posición
            position_text = f"{self.selected_index + 1} / {len(self.song_folders)}"
            pos_surface = indicator_font.render(position_text, True, (180, 180, 180))
            pos_rect = pos_surface.get_rect(center=(self.width // 2, folder_area_top + self.visible_count * folder_item_height + 35))
            surface.blit(pos_surface, pos_rect)

        # --- Controles en la parte inferior ---
        controls_font = pygame.font.Font(None, 26)
        controls_lines = [
            "LEFT/RIGHT : Cambiar BPM ±1",
            "UP/DOWN : Seleccionar canción",
            "ENTER : Elegir canción",
            "ESC : Volver al menú"
        ]
        controls_start_y = self.height - 140

        for i, line in enumerate(controls_lines):
            text_surface = controls_font.render(line, True, (180, 180, 180))
            text_rect = text_surface.get_rect(center=(self.width // 2, controls_start_y + i * 30))
            surface.blit(text_surface, text_rect)

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.FULLSCREEN

    @property
    def is_transient(self) -> bool:
        return False