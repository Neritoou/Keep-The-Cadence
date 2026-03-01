import pygame
from typing import TYPE_CHECKING
from enfocate import SCREEN_SIZE

from .game_state import GameState
from .types import StateID, OverlayType
from ..util.conversors import get_hint_key

if TYPE_CHECKING:
    from ..core.game import Game

class CreditsState(GameState):
    """Estado que muestra los créditos del juego en una imagen estática."""
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.w, self.h = SCREEN_SIZE

        self.bg_credits = self.game.resources.get_image("Background3") 
        
        self.font_small = self.game.resources.get_font("Alternative", 35)
        
        self._build_static_surfaces()

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "back") or self.game.input.is_action_pressed("ui", "select"):
            self.game.audio.play_sfx("select")
            self.game.state.exit_current()

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.bg_credits, (0, 0))

        self._draw_hint_bar(surface)

    def _draw_hint_bar(self, surface: pygame.Surface) -> None:
        bar_y = self.h - 50
        surface.blit(self._hint_bar, (0, bar_y))

        gap = 3
        total_w = self._hint_renders[0].get_width() + self._hint_renders[1].get_width() + self._hint_renders[2].get_width()
        total_w += gap * (len(self._hint_renders) - 1)

        cur_x = (self.w - total_w) // 2
        text_y = bar_y + 6
        
        surface.blit(self._hint_renders[0], (cur_x, text_y))
        cur_x += self._hint_renders[0].get_width() + gap
        surface.blit(self._hint_renders[1], (cur_x, text_y))
        cur_x += self._hint_renders[1].get_width() + gap
        surface.blit(self._hint_renders[2], (cur_x, text_y))

    def _build_static_surfaces(self) -> None:
        """Pre-genera la barra y el texto del hint."""
        self._hint_bar = pygame.Surface((self.w, 50), pygame.SRCALPHA)
        self._hint_bar.fill((8, 4, 18))
        
        BD_PANEL = (110, 80, 200, 160) # Violeta
        pygame.draw.line(self._hint_bar, BD_PANEL, (0, 0), (self.w, 0), 1)
        
        k_config = self.game.controls_config
        key_str1 = get_hint_key(k_config, "back")
        key_str2 = get_hint_key(k_config, "select")
        
        p = self.font_small.render(f"Presiona", True, (150, 135, 190))
        k = self.font_small.render(f" [{key_str1}] o [{key_str2}]", True, (190, 165, 255))
        a = self.font_small.render(f" para volver al menu.", True, (150, 135, 190))

        self._hint_renders: tuple[pygame.Surface, pygame.Surface, pygame.Surface] = (p, k, a)

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.FULLSCREEN

    @property
    def is_transient(self) -> bool:
        return False