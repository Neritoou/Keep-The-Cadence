import pygame
from typing import TYPE_CHECKING
from .game_state import GameState
from .types import OverlayType, StateID

from ..core.chart_player import ChartLoader, ChartPlayer
from ..core.note import NoteInputHandler
from ..core.scoring import ScoreManager
from ..core.types import Judgement, NoteDirection
from ..core.difficulty_data import DIFFICULTY_DATA

from ..constants import SPAWN_TIME_MS, MIKU_PLAY_POSITION
from ..ui import PerformanceBar, UILabel, UIManager, UIJudgementLabel

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

        self.score_manager = ScoreManager(self.chart.total_notes, self.diff_data)

        self.note_input = NoteInputHandler(
            self.player, self.game.note_renderer, self.game.character,
            self.score_manager
            )

        self._build_fonts()
        self._build_ui()

    def start_game(self) -> None:
        """Llamado por CountdownState al terminar. Arranca el juego de verdad."""
        self.game.note_renderer.reset_receptors()
        self.performance_bar.snap()
        self.player.play()

    def is_game_over(self) -> bool:
        return self.score_manager.performance <= 0.00
    
    def restart(self) -> None:
        """Reinicia la partida desde el segundo 0 sin crear una nueva instancia."""
        self.player.stop()
        self.player.reset()
        self.score_manager.reset()
        self.performance_bar.set_performance(self.score_manager.performance_ratio)
        self.performance_bar.snap()
        self.note_input.reset()
        self.game.character.set_position(MIKU_PLAY_POSITION)
        self.game.character.reset()
        self.game.bg_normies.reset()
        self.game.bg_normies.play("bg", reset=True, loop=True)
        self.game.character.animator.play("idle", reset=True, loop=True)
        self.game.note_renderer.reset_receptors()
        self.judgement_label.visible = False
        self.game.state.change(StateID.COUNTDOWN, play_state=self)

    def on_enter(self) -> None:
        self.game.character.set_position(MIKU_PLAY_POSITION)
        self.game.character.reset()
        self.game.bg_normies.reset()
        self.game.bg_normies.sync_to_bpm(self.chart.bpm)
        self.game.character.update_bpm(self.chart.bpm)
        self.game.character.animator.play("idle",reset=True, loop=True)
        self.game.bg_normies.play("bg", reset=True, loop=True)
        self.game.state.change(StateID.COUNTDOWN, play_state=self)

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
        self.score_label.set_text(f"Puntuacion: {self.score_manager.score}")
        self.misses_label.set_text(f"|   Fallos: {self.score_manager.judgement_counts[Judgement.MISS]}")

        self.ui.update(dt)

        if self.is_game_over():
            direction = self.game.character.receptor.direction or NoteDirection.UP
            self.game.state.change(StateID.GAME_OVER,direction=direction, play_state=self)
            return
            
        if self.player.is_finished:
            self.game.state.change(StateID.WIN, play_state=self)
    
    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "pause"):
            self.player.pause()
            self.game.state.change(StateID.PAUSE, play_state=self)
            return

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
    
    def _build_fonts(self) -> None:
        self.fonts = {
            "small": self.game.resources.get_font("Estandar", 30),
            "normal": self.game.resources.get_font("Estandar", 48)
        }

    def _build_ui(self) -> None:
        performance_icon = self.game.resources.get_spritesheet("PerformanceIcon")
        self.performance_bar = PerformanceBar("performance_bar", 590, 600, 600, performance_icon, icon_lerp_speed=5.0)

        self.judgement_label = UIJudgementLabel("judgement_label", 560, 130, self.fonts["normal"])

        self.score_label = UILabel("score_label", 880, 650, "Puntuacion: 0", self.fonts["small"], "#FFFFFF")
        self.misses_label = UILabel("misses_label", 1100, 650, "|   Fallos: 0", self.fonts["small"], "#FFFFFF")
        
        self.panel = self.game.resources.get_image("stage_panel")
        self.panel_rect = self.panel.get_rect(center = (540,710))


        self.ui: UIManager = UIManager()
        self.ui.add_element(self.performance_bar)
        self.ui.add_element(self.score_label)
        self.ui.add_element(self.misses_label)
        self.ui.add_element(self.judgement_label)

        self.note_input._on_judgement = self.judgement_label.show_judgement

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE

    @property
    def is_transient(self) -> bool:
        return False