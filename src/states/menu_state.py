import pygame
from typing import TYPE_CHECKING

from .types import StateID, OverlayType
from .game_state import GameState

from enfocate import SCREEN_SIZE
from ..ui import UIManager, UISlideMenu, UILabel

if TYPE_CHECKING:
    from src.core.game import Game

class MenuState(GameState):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)

        options_list =[
            ("JUGAR", self._on_play),
            ("EDITOR DE CHART", self._on_editor),
            ("CREDITOS", self._on_credits),
            ("SALIR", self._on_exit)
        ]
        screen_center_w = SCREEN_SIZE[0] // 2

        self.font1 = self.game.resources.get_font("Cursive", 130)
        self.font2 = self.game.resources.get_font("Estandar", 48)

        self.bg = self.game.resources.get_image("Background")
        
        splashart = self.game.resources.get_image("SplashArt")
        self.splashart = pygame.transform.smoothscale(splashart, (933, 698))
        
        self.title = self.game.resources.get_image("Title")

        btn_surface = pygame.Surface((700, 80), pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, (255, 210, 210), btn_surface.get_rect(), border_radius=45)

        sel_surface = pygame.Surface((700, 80), pygame.SRCALPHA)
        pygame.draw.rect(sel_surface, (255, 210, 210), sel_surface.get_rect(), border_radius=45)
        pygame.draw.rect(sel_surface, (60, 40, 40), sel_surface.get_rect(), width=5, border_radius=45)

        self.menu = UISlideMenu(
            "main_menu", 550, 325, options_list, btn_surface, self.font2,
            (60, 40, 40), selected_surface=sel_surface, content_padding=50, spacing=10, hidden_offset=160
        )
        
        self.ui: UIManager = UIManager()
        self.ui.add_element(self.menu)
        
    def on_enter(self) -> None:
        pass
    
    def on_exit(self) -> None:
        return

    def update(self, dt: float) -> None:
        self.ui.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.bg, (0, 0))
        surface.blit(self.splashart, (400, 80))
        surface.blit(self.title, (52, 41))

        self.ui.render(surface)

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "up"):
            self.menu.move_up()
        if self.game.input.is_action_pressed("ui", "down"):
            self.menu.move_down()
        if self.game.input.is_action_pressed("ui", "select"):
            self.menu.execute_selected()
            
    
    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE

    @property
    def is_transient(self) -> bool:
        return False
    


    # --- Callbacks ---
    def _on_play(self):
        self.game.state.change_with_transition(StateID.SONG_SELECT)
    
    def _on_editor(self):
        self.game.state.change(StateID.CHART_SETUP)

    def _on_credits(self):
        print("ESCENA DE CREDITOS")
    
    def _on_exit(self):
        self.game._stop_context()