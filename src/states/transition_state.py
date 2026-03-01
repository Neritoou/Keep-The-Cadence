import pygame
from typing import TYPE_CHECKING
from .game_state import GameState
from .types import StateID, OverlayType
from enfocate import SCREEN_SIZE

if TYPE_CHECKING:
    from ..core.game import Game

# Duración total: 400ms — 200ms fade out + 200ms fade in
HALF_DURATION_MS = 400.0

class TransitionState(GameState):
    """Overlay de transición con fade a negro entre dos estados."""
    def __init__(self, game: "Game", target: StateID, kwargs: dict | None = None):
        super().__init__(game)
        self._target    = target
        self._kwargs    = kwargs or {}

        self._elapsed   = 0.0       # ms acumulados en la fase actual
        self._alpha     = 0         # 0 = transparente, 255 = negro total
        self._phase     = "out"     # "out" -> "in"
        self._switched  = False     # True cuando ya cambió al estado destino

        # Superficie negra que se superpone
        self._overlay = pygame.Surface((SCREEN_SIZE[0], SCREEN_SIZE[1]))
        self._overlay.fill((0, 0, 0))

    def on_exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        self._elapsed += dt * 1000

        progress = min(self._elapsed / HALF_DURATION_MS, 1.0)
        self._alpha = int(progress * 255) if self._phase == "out" else int((1.0 - progress) * 255)

        if progress >= 1.0 and self._phase == "out":
            self._switch()

    def _switch(self) -> None:
        self.game.state.exit_current() 
        self.game.state.change(self._target, **self._kwargs) 
        self._phase   = "in"
        self._elapsed = 0.0

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        pass  # Bloquea todo input durante la transición

    def render(self, surface: pygame.Surface) -> None:
        self._overlay.set_alpha(self._alpha)
        surface.blit(self._overlay, (0, 0))

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.SEMITRANSPARENT  # renderiza el estado de abajo

    @property
    def is_transient(self) -> bool:
        return True