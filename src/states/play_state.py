import pygame
from typing import TYPE_CHECKING

from .game_state import GameState
from .types import OverlayType, StateID

from ..core.chart_player import ChartLoader, ChartPlayer
from ..core.note_renderer import NoteRenderer
from ..core.types import ScrollDirection

from ..constants import HIT_LINE_XS, HIT_LINE_Y_UP, SPAWN_TIME_MS
from ..util.paths import get_full_song_path

if TYPE_CHECKING:
    from src.core.game import Game


class PlayState(GameState):
    """Estado principal del juego donde se reproduce el chart."""
    def __init__(self, game: "Game", song_folder: str):
        super().__init__(game)
        self.song_folder = song_folder

        # Carga la canción
        try:
            self.song_path = str(get_full_song_path(song_folder))
        except FileNotFoundError as e:
            raise RuntimeError(f"PlayState: No se pudo cargar la canción: {e}")
        
        # Carga el chart
        try:
            self.chart = ChartLoader.load_from_song_folder(song_folder)
        except (FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"PlayState: Error cargando chart: {e}")
        
        self.player = ChartPlayer(
            self.chart, game.audio,
            self.song_path, SPAWN_TIME_MS
        )

        notes_data = game.resources.get_all_notes()
        self.renderer = NoteRenderer(
            notes_data, HIT_LINE_XS, HIT_LINE_Y_UP,
            ScrollDirection.UP, SPAWN_TIME_MS, 720
        )

        # (!) Quitar cuando no se necesite el debug
        self.debug_font = pygame.font.Font(None, 24)

        self.player.play()

    def on_enter(self) -> None:
        print(f"PlayState: Iniciando gameplay para '{self.song_folder}'.")

    def on_exit(self) -> None:
        self.player.stop()
        print("PlayState: Saliendo del gameplay.")

    def on_resume(self) -> None:
        self.player.resume()
    
    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "pause"):
            #self.player.toggle_play_pause()

            # (!) Si quieres que sea mas rapido -sin la pantalla de pausa- comenta los dos de abajo
            # (!) y descomenta el de arriba para que se alterne el play/pause con el espacio

            self.player.pause()
            self.game.state.change(StateID.PAUSE, song_folder=self.song_folder)
            return

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 20, 40))
        active_notes = self.player.get_active_notes()

        self.renderer.draw_receptors(surface)

        # Notas en movimiento
        self.renderer.draw_notes(
            surface, active_notes,
            self.player.current_time,
            self.chart.pixels_per_ms,
        )

        self._draw_debug_info(surface)

    def update(self, dt: float) -> None:
        self.player.update(dt)
        self.renderer.update(dt)
        
        if self.player.is_finished:
            print(f"PlayState: Chart '{self.song_folder}' completado!")
            self.game.state.change(StateID.MENU)

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE

    @property
    def is_transient(self) -> bool:
        return False
    

    # Método Provisional para debug
    def _draw_debug_info(self, surface: pygame.Surface) -> None:
        current_section = self.player.get_current_section()
        section_info = f"Sección {current_section.index + 1}" if current_section else "N/A"
        
        active_notes = self.player.get_active_notes()
        
        info_lines = [
            f"Canción: {self.song_folder}",
            f"Tiempo: {self.player.current_time / 1000:.2f}s / {self.chart.total_duration / 1000:.2f}s",
            f"Progreso: {self.player.get_progress_percentage():.1f}%",
            f"BPM: {self.chart.bpm}",
            f"{section_info}",
            f"Notas visibles: {len(active_notes)}",
            f"Estado: {'▶ REPRODUCIENDO' if self.player.is_playing else '⏸ PAUSADO'}",
            "",
            "SPACE/p: Pausar",
        ]
        
        y = 10
        for line in info_lines:
            text = self.debug_font.render(line, True, (255, 255, 255))
            surface.blit(text, (10, y))
            y += 25