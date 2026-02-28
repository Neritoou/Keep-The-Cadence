import pygame
from typing import TYPE_CHECKING

from .types import StateID, OverlayType
from .game_state import GameState
from ..ui import UIManager, UISlideMenu, UILabel

if TYPE_CHECKING:
    from src.core.game import Game

class OptionsState(GameState):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)

        self.font_title = self.game.resources.get_font("Alternative", 100)
        self.font_menu = self.game.resources.get_font("Estandar", 48)

        self.bg = self.game.resources.get_image("Background2")

        self._build_ui()
        
    def on_enter(self) -> None:
        pass
    
    def on_exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        self.ui.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.bg, (0, 0))

        self.ui.render(surface)

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "up"):
            self.menu.move_up()
        elif self.game.input.is_action_pressed("ui", "down"):
            self.menu.move_down()
        elif self.game.input.is_action_pressed("ui", "select"):
            self.menu.execute_selected()
        elif self.game.input.is_action_pressed("ui", "pause"): # ESC para volver
            self._on_back()
            
    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE

    @property
    def is_transient(self) -> bool:
        return False
    
    def _build_ui(self) -> None:
        options_list = [
            ("CONTROLES", self._on_controls),
            ("EDITOR DE CHART", self._on_chart_editor),
            ("BORRAR DATOS", self._on_reset_data),
            ("VOLVER", self._on_back)
        ]

        # Título del menú de opciones
        self.title = UILabel("options_title", 70, 50, 
                             "Opciones", self.font_title, (60, 40, 40), center=False)

        btn_surface = pygame.Surface((700, 80), pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, (213, 176, 191), btn_surface.get_rect(), border_radius=45)

        sel_surface = pygame.Surface((700, 80), pygame.SRCALPHA)
        pygame.draw.rect(sel_surface, (213, 176, 191), sel_surface.get_rect(), border_radius=45)
        pygame.draw.rect(sel_surface, (60, 40, 40), sel_surface.get_rect(), width=5, border_radius=45)

        self.menu = UISlideMenu(
            "options_menu", 640, 220, options_list, btn_surface, self.font_menu,
            (60, 40, 40), selected_surface=sel_surface, 
            content_padding=50, spacing=20, hidden_offset=160
        )
        
        self.ui: UIManager = UIManager()
        self.ui.add_element(self.title)
        self.ui.add_element(self.menu)



    # --- Callbacks ---
    def _on_controls(self):
        self.game.state.change(StateID.KEYBIND_EDITOR)
    
    def _on_chart_editor(self):
        self.game.state.change_with_transition(StateID.CHART_SETUP)

    def _on_reset_data(self):
        self.game.database.reset_all_records()
        print("¡Datos borrados con éxito!")
    
    def _on_back(self):
        self.game.state.change(StateID.MENU)