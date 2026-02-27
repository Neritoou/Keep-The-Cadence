import pygame
from enfocate import SCREEN_SIZE, COLORS

from typing import TYPE_CHECKING
from .game_state import GameState
from .types import StateID, OverlayType

from ..ui import UIMenu, UILabel, UIManager

if TYPE_CHECKING:
    from ..core.game import Game
    from ..states import PlayState



class PauseState(GameState):
    """Estado de pausa que se superpone al juego."""
    def __init__(self, game: "Game", play_state: "PlayState"):
        super().__init__(game)
        self.play_state = play_state

        screen_center_w = SCREEN_SIZE[0] // 2

        font_title = self.game.resources.get_font("Cursive", 100)
        font_menu = self.game.resources.get_font("Estandar", 48)
        
        self.title = UILabel("pause_title", screen_center_w, 170,
            "Pausa", font_title, COLORS["coral_pastel"])

        options = [
            ("CONTINUAR", self._on_resume),
            ("REINICIAR", self._on_restart),
            ("VOLVER AL MENU", self._on_menu),
        ]
        
        self.menu = UIMenu("pause_menu", screen_center_w, 360,
            options, font_menu, spacing=80, center_text=True
        )

        self.ui: UIManager = UIManager()
        self.ui.add_element(self.title)
        self.ui.add_element(self.menu)
    
    def on_enter(self) -> None:
        pass
    
    def on_exit(self) -> None:
        pass
    
    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "up"):
            self.menu.move_up()
        elif self.game.input.is_action_pressed("ui", "down"):
            self.menu.move_down()
        elif self.game.input.is_action_pressed("ui", "select"):
            self.menu.execute_selected()
        elif  self.game.input.is_action_pressed("ui", "pause"):
            self._on_resume()
    
    def update(self, dt: float) -> None:
        """Actualiza el menú de pausa."""
        self.ui.update(dt)
    
    def render(self, surface: pygame.Surface) -> None:
        # Fondo semitransparente oscuro
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        self.ui.render(surface)
    

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.SEMITRANSPARENT
    
    @property
    def is_transient(self) -> bool:
        return False
    


    # --- Callbacks ---
    def _on_resume(self):
        """Continúa el juego."""
        self.game.state.exit_current()
    
    def _on_restart(self):
        self.play_state.restart()
        self.game.state.exit_current()
    
    def _on_menu(self):
        """Vuelve al menú principal."""
        self.game.state.clear()
        self.game.state.change(StateID.MENU)