import pygame
from enfocate import SCREEN_SIZE

from typing import TYPE_CHECKING
from .game_state import GameState
from .types import StateID, OverlayType

from ..ui import UIButtonMenu, UILabel, UIManager

if TYPE_CHECKING:
    from ..core.game import Game
    from ..states import PlayState



class PauseState(GameState):
    """Estado de pausa que se superpone al juego."""
    def __init__(self, game: "Game", play_state: "PlayState"):
        super().__init__(game)

        self.play_state = play_state

        self._build_fonts()
        self._build_ui()
    
    def on_enter(self) -> None:
        pass
    
    def on_exit(self) -> None:
        pass

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "up"):
            self.game.audio.play_sfx("scroll")
            self.menu.move_up()

        elif self.game.input.is_action_pressed("ui", "down"):
            self.game.audio.play_sfx("scroll")
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
        overlay.set_alpha(190)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        self.ui.render(surface)
    

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.SEMITRANSPARENT
    
    @property
    def is_transient(self) -> bool:
        return False
    
    def _build_fonts(self) -> None:
        self.fonts = {
            "title": self.game.resources.get_font("Cursive", 130),
            "menu": self.game.resources.get_font("Estandar", 48)
        }

    def _build_ui(self) -> None:
        screen_center_w = SCREEN_SIZE[0] // 2
        
        self.title = UILabel("pause_title", screen_center_w, 100,
            "Pausa", self.fonts["title"], "#8af2f2")

        options = [
            ("Continuar", self._on_resume),
            ("Reiniciar", self._on_restart),
            ("Opciones", self._on_options),
            ("Otra cancion", self._on_menu)
        ]
        
        btn_surface = pygame.Surface((370, 60), pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, (50, 40, 70), btn_surface.get_rect(), border_radius=45)

        sel_surface = pygame.Surface((370, 60), pygame.SRCALPHA)
        pygame.draw.rect(sel_surface, (110, 80, 200), sel_surface.get_rect(), border_radius=45)
        pygame.draw.rect(sel_surface, (255, 255, 255), sel_surface.get_rect(), width=5, border_radius=45) 

        self.menu = UIButtonMenu(
            "pause_menu", screen_center_w, 330, options, btn_surface,
            sel_surface, self.fonts["menu"], (255, 255, 255), center_x=True, spacing=20
        )

        self.ui: UIManager = UIManager()
        self.ui.add_element(self.title)
        self.ui.add_element(self.menu)



    # --- Callbacks ---
    def _on_resume(self):
        """Continúa el juego."""
        self.game.audio.play_sfx("select")
        self.game.state.exit_current()
    
    def _on_restart(self):
        self.game.audio.play_sfx("start")
        self.game.state.exit_current()
        self.play_state.restart()
    
    def _on_menu(self):
        """Vuelve al menú principal."""
        self.game.audio.play_sfx("start")
        self.game.state.clear()
        self.game.state.change(StateID.SONG_SELECT)

    def _on_options(self):
        """Vuelve al menú principal."""
        self.game.audio.play_sfx("select")
        self.game.state.change(StateID.OPTIONS)