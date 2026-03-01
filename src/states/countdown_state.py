import pygame
from typing import TYPE_CHECKING
from .types import OverlayType
from .game_state import GameState
from ..resources.types import AudioCategory
from enfocate import SCREEN_SIZE

if TYPE_CHECKING:
    from src.core.game import Game
    from .play_state import PlayState


COUNTDOWN_STEPS = ["3", "2", "1", "¡GO!"]
STEP_DURATION   = 1.0
GO_DURATION     = 0.6
INITIAL_DELAY   = 0.5


class CountdownState(GameState):
    """
    Estado de cuenta regresiva antes de que el juego comience.
    Muestra 3 → 2 → 1 → ¡GO!
    """

    def __init__(self, game: "Game", play_state: "PlayState"):
        super().__init__(game)
        self.play_state = play_state

        self._steps     = list(COUNTDOWN_STEPS)
        self._step_text = self._steps.pop(0)
        self._duration  = STEP_DURATION
        self._elapsed   = 0.0
        self._waiting   = True

        # Overlay negro semitransparente.
        self._overlay = pygame.Surface(SCREEN_SIZE)
        self._overlay.set_alpha(150)
        self._overlay.fill((0, 0, 0))


        self._sounds: list[str] = [f"countdown_{i}" for i in range(0, 4)]

        # (?) cambiar por font del resource manager cuando esté disponible
        self.font = pygame.font.SysFont("Consolas", 120, bold=True)

    def _play_current_sound(self) -> None:
        sound_index = len(self._steps)  # 3 → 2 → 1 → 0
        self.game.audio.play_sfx(self._sounds[sound_index])

    def on_enter(self) -> None:
        pass
    
    def on_exit(self) -> None:
        self.play_state.start_game()

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        pass

    def update(self, dt: float) -> None:
        self.play_state.game.bg_normies.update(dt)
        self.play_state.game.character.update(dt)
        self._elapsed += dt

        if self._waiting:
            if self._elapsed >= INITIAL_DELAY:
                self._waiting = False
                self._elapsed = 0.0
                self._play_current_sound()
            return

        if self._elapsed >= self._duration:
            if self._steps:
                self._step_text = self._steps.pop(0)
                self._duration  = GO_DURATION if self._step_text == "¡GO!" else STEP_DURATION
                self._elapsed   = 0.0
                self._play_current_sound()
            else:
                self.game.state.exit_current()

    def render(self, surface: pygame.Surface) -> None:
        self.game.bg_normies.draw(surface,(0,0))
        surface.blit(self.play_state.panel,self.play_state.panel_rect)
        self.game.character.draw(surface)
        surface.blit(self._overlay, (0, 0))

        if self._waiting:
            return

        text_surf = self.font.render(self._step_text, True, (255, 255, 255))
        rect = text_surf.get_rect(center=(surface.get_width() // 2,
                                          surface.get_height() // 2))
        surface.blit(text_surf, rect)

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.FULLSCREEN

    @property
    def is_transient(self) -> bool:
        return False