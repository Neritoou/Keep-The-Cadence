import pygame
from typing import TYPE_CHECKING

from .game_state import GameState
from .types import OverlayType, StateID
from ..resources.types import AudioCategory

from ..core.chart_player import ChartLoader, ChartPlayer
from ..core.note_input_handler import NoteInputHandler
from ..core.scoring import ScoreManager
from ..core.types import Judgement

from ..constants import SPAWN_TIME_MS
from ..ui import PerformanceBar, UILabel, UIManager

if TYPE_CHECKING:
    from ..core.game import Game
    from ..database import DifficultyName



class PlayState(GameState):
    """Estado principal del juego donde se reproduce el chart."""
    def __init__(self, game: "Game", song_folder: str, song_id: int, difficulty: "DifficultyName"):
        super().__init__(game)
        self.song_id = song_id
        self.song_folder = song_folder
        self.diff = difficulty
        self.chart = ChartLoader.load_chart_from_json(song_folder)

        self.player = ChartPlayer(self.chart, game.audio, song_folder, SPAWN_TIME_MS)

        sounds = tuple(self.game.resources.get_sound(f"miss_note_{i}", AudioCategory.SFX)
            for i in range(1, 4)
            )

        self.score_manager = ScoreManager(self.chart.total_notes)
        self.note_input = NoteInputHandler(
            self.player, self.game.note_renderer, self.game.character, sounds,
            self.score_manager
            )

        performance_icon = game.resources.get_spritesheet("PerformanceIcon")
        self.performance_bar = PerformanceBar("performance_bar", 340, 600, 600, performance_icon, icon_lerp_speed=5.0)

        font = game.resources.get_font("Estandar", 30)

        self.score_label = UILabel("score_label", 675, 650, "SCORE: 0", font, "#808080")
        self.misses_label = UILabel("misses_label", 870, 650, "|   MISSES: 0", font, "#808080")

        self.ui: UIManager = UIManager()
        self.ui.add_element(self.performance_bar)
        self.ui.add_element(self.score_label)
        self.ui.add_element(self.misses_label)

        # (!) Quitar cuando no se necesite el debug
        self.debug_font = pygame.font.Font(None, 24)

        self.game.character.update_bpm(self.chart.bpm)
        self.player.play()

    # (!) Ver donde se va a ubicar
    def is_game_over(self) -> bool:
        return self.score_manager.performance <= 0.00

    def on_enter(self) -> None:
        self.game.character.reset()
        self.game.note_renderer.reset_receptors()

        self.game.character.update_bpm(self.chart.bpm)
        self.game.character.animator.play("idle",reset=True, loop=True)
        self.player.play()

    def on_exit(self) -> None:
        self.player.stop()
        self.player.reset()
        self.player.cleanup()
    
    def on_resume(self) -> None:
        self.player.resume()

    def update(self, dt: float) -> None:
        self.player.update(dt)
        self.game.note_renderer.update(dt)
        self.game.character.update(dt)
        self.note_input.update(dt)

        self.performance_bar.set_performance(self.score_manager.performance_ratio)
        self.score_label.set_text(f"SCORE: {self.score_manager.score}")
        self.misses_label.set_text(f"|   MISSES: {self.score_manager.judgement_counts[Judgement.MISS]}")

        self.ui.update(dt)

        if self.is_game_over():
            self.game.state.change(StateID.GAME_OVER, final_score=self.score_manager.score, song_folder=self.song_folder)

        if self.player.is_finished:
            self.game.state.change(StateID.WIN, final_score=self.score_manager.score, song_folder=self.song_folder)
    
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

        self.ui.render(surface)

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
            f"Performance: {self.score_manager.performance:.1f}%",
            f"Score: {self.score_manager.score}",
            f"Combo: {self.score_manager.combo}",
            "",
            "SPACE/p: Pausar",
        ]
        
        y = 10
        for line in info_lines:
            text = self.debug_font.render(line, True, (255, 255, 255))
            surface.blit(text, (10, y))
            y += 25