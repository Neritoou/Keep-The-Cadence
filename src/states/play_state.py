import pygame
from typing import TYPE_CHECKING

from .game_state import GameState
from .types import OverlayType, StateID
from ..resources.types import AudioCategory

from ..core.chart_player import ChartLoader, ChartPlayer
from ..core.note_renderer import NoteRenderer
from ..core.types import ScrollDirection, NoteDirection
from ..core.note_input_handler import NoteInputHandler

from ..constants import HIT_LINE_XS, HIT_LINE_Y_UP, SPAWN_TIME_MS, MISS_DISPLAY

if TYPE_CHECKING:
    from ..core.game import Game


class PlayState(GameState):
    """Estado principal del juego donde se reproduce el chart."""
    def __init__(self, game: "Game", song_folder: str):
        super().__init__(game)
        self.song_folder = song_folder
        self.chart = ChartLoader.load_chart_from_json(song_folder)

        self.player = ChartPlayer(self.chart, game.audio, song_folder, SPAWN_TIME_MS)

        sounds = tuple(self.game.resources.get_sound(f"miss_note_{i}", AudioCategory.SFX)
            for i in range(1, 4)
            )

        self.note_input = NoteInputHandler(self.player,self.game.note_renderer,self.game.character,sounds)

        # (!) Quitar cuando no se necesite el debug
        self.debug_font = pygame.font.Font(None, 24)
        self.game.character.update_bpm(self.chart.bpm)
        self.player.play()

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        self.player.stop()
        self.player.cleanup()
    
    def on_resume(self) -> None:
        self.player.resume()

    def update(self, dt: float) -> None:
        self.player.update(dt)
        self.game.note_renderer.update(dt)
        self.game.character.update(dt)
        self.note_input.update(dt)

        if self.player.is_finished:
            self.game.state.change(StateID.MENU)
            
    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "pause"):
            self.player.pause()
            self.game.state.change(StateID.PAUSE, song_folder=self.song_folder)
            return
        
        # --- Teclas de notas ---
        for action, direction in self.game._PLAY_ACTIONS:
            if self.game.input.is_action_pressed("play", action):
                self.note_input.on_key_press(direction)
            elif self.game.input.is_action_released("play", action):
                self.note_input.on_key_release(direction)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 20, 40))
        # Notas en movimiento
        self.game.note_renderer.draw_notes(
            surface, self.player._active_notes,
            self.player.current_time,
            self.chart.pixels_per_ms,
        )

        self.game.note_renderer.draw_receptors(surface)


        self.game.character.draw(surface)
        self._draw_debug_info(surface)

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE

    @property
    def is_transient(self) -> bool:
        return False
    
    # Método Provisional para debug
    def _draw_debug_info(self, surface: pygame.Surface) -> None:
        section_info = f"Sección {self.player.current_section.index + 1}"
        
        info_lines = [
            f"Canción: {self.song_folder}",
            f"Tiempo: {self.player.current_time / 1000:.2f}s / {self.chart.song_duration / 1000:.2f}s",
            f"Progreso: {self.player.get_progress_percentage():.1f}%",
            f"BPM: {self.chart.bpm}",
            f"Notas Activas: {len(self.player._active_notes)}",
            f"{section_info}",
            f"Estado: {'REPRODUCIENDO' if self.player.is_playing else 'PAUSADO'}",
            "",
            "SPACE/p: Pausar",
        ]
        
        y = 10
        for line in info_lines:
            text = self.debug_font.render(line, True, (255, 255, 255))
            surface.blit(text, (10, y))
            y += 25

 # --- INPUT ---

