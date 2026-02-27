import pygame
from typing import TYPE_CHECKING

from .game_state import GameState
from .types import OverlayType, StateID
from ..resources.types import AudioCategory

from ..core.chart_player import ChartLoader, ChartPlayer
from ..core.note_input_handler import NoteInputHandler
from ..core.scoring import ScoreManager
from ..core.types import Judgement
from ..core.difficulty_data import DIFFICULTY_DATA

from ..constants import SPAWN_TIME_MS, MIKU_PLAY_POSITION
from ..ui import PerformanceBar, UILabel, UIManager

if TYPE_CHECKING:
    from ..core.game import Game
    from ..core.database import DifficultyName



class PlayState(GameState):
    """Estado principal del juego donde se reproduce el chart."""
    def __init__(self, game: "Game", song_folder: str, song_id: int, difficulty: "DifficultyName"):
        super().__init__(game)
        self.song_id = song_id
        self.song_folder = song_folder
        self.chart = ChartLoader.load_chart_from_json(song_folder)
        self.diff = difficulty
        self.diff_data = DIFFICULTY_DATA[difficulty.value]
        # Se actualiza los pixeles por segundo según la dificultad
        self.pixels_per_ms = self.chart.pixels_per_ms * self.diff_data.pixels_per_ms_mult

        self.player = ChartPlayer(self.chart, game.audio, song_folder, SPAWN_TIME_MS, diff_data = self.diff_data)

        sounds = tuple(self.game.resources.get_sound(f"miss_note_{i}", AudioCategory.SFX)
            for i in range(1, 4)
            )

        self.score_manager = ScoreManager(self.chart.total_notes, self.diff_data)

        self.note_input = NoteInputHandler(
            self.player, self.game.note_renderer, self.game.character, sounds,
            self.score_manager
            )

        performance_icon = game.resources.get_spritesheet("PerformanceIcon")
        self.performance_bar = PerformanceBar("performance_bar", 590, 600, 600, performance_icon, icon_lerp_speed=5.0)

        font = game.resources.get_font("Estandar", 30)

        self.score_label = UILabel("score_label", 905, 650, "SCORE: 0", font, "#FFFFFF")
        self.misses_label = UILabel("misses_label", 1100, 650, "|   MISSES: 0", font, "#FFFFFF")

        self.panel = self.game.resources.get_image("stage_panel")
        self.panel_rect = self.panel.get_rect(center = (540,710))

        self.ui: UIManager = UIManager()
        self.ui.add_element(self.performance_bar)
        self.ui.add_element(self.score_label)
        self.ui.add_element(self.misses_label)

    # (!) Ver donde se va a ubicar
    def is_game_over(self) -> bool:
        return self.score_manager.performance <= 0.00

    def on_enter(self) -> None:
        self.game.character.set_position(MIKU_PLAY_POSITION)
        self.game.character.reset()
        self.game.note_renderer.reset_receptors()
        self.game.bg_normies.sync_to_bpm(self.chart.bpm)
        self.game.character.update_bpm(self.chart.bpm)
        self.game.character.animator.play("idle",reset=True, loop=True)
        self.game.bg_normies.play("bg", reset=True, loop=True)
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
        self.game.bg_normies.update(dt)
        self.game.character.update(dt)
        self.note_input.update(dt)

        self.performance_bar.set_performance(self.score_manager.performance_ratio)
        self.score_label.set_text(f"SCORE: {self.score_manager.score}")
        self.misses_label.set_text(f"|   MISSES: {self.score_manager.judgement_counts[Judgement.MISS]}")

        self.ui.update(dt)

        if self.is_game_over():
            self.game.state.change(StateID.GAME_OVER, final_score=self.score_manager.score, play_state=self)

        if self.player.is_finished:
            self.game.state.change(StateID.WIN, play_state=self)
    
    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "pause"):
            self.player.pause()
            self.game.state.change(StateID.PAUSE, play_state=self)
            return
        
        # (!) DEBUG — quitar cuando no se necesite
        elif self.game.input.is_key_pressed(pygame.K_F1):
            self.player.stop()
            self.game.audio.stop_all_sounds()
            self.game.audio.stop_music
            counts = {
            Judgement.PERFECT: 120,
            Judgement.GOOD:    30,
            Judgement.BAD:     10,
            Judgement.MISS:    5,
            }
            for judgement, times in counts.items():
                for _ in range(times):
                    self.score_manager.register_tap(judgement)
            self.game.state.change(StateID.WIN, play_state=self)
        
        # --- Teclas de notas ---
        for action, direction in self.game._PLAY_ACTIONS:
            if self.game.input.is_action_pressed("play", action):
                self.note_input.on_key_press(direction)
            elif self.game.input.is_action_released("play", action):
                self.note_input.on_key_release(direction)

    def render(self, surface: pygame.Surface) -> None:
        self.game.bg_normies.draw(surface,(0,0))
        surface.blit(self.panel,self.panel_rect)

        # Notas en movimiento
        self.game.note_renderer.draw_notes(
            surface, self.player._active_notes,
            self.player.current_time,
            self.pixels_per_ms,
        )

        self.game.note_renderer.draw_receptors(surface)


        self.game.character.draw(surface)
        self.ui.render(surface)

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE

    @property
    def is_transient(self) -> bool:
        return False

    def restart(self) -> None:
        """Reinicia la partida desde el segundo 0 sin crear una nueva instancia."""
        self.player.stop()
        self.player.reset()

        self.score_manager.reset()
        self.note_input.reset()

        self.game.character.set_position(MIKU_PLAY_POSITION)
        self.game.character.reset()
        self.game.note_renderer.reset_receptors()
        self.game.character.animator.play("idle", reset=True, loop=True)

        self.player.play()