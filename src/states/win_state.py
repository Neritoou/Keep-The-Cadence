import pygame
from typing import TYPE_CHECKING
from enfocate import SCREEN_SIZE

from .game_state import GameState
from .types import StateID, OverlayType
from ..ui import UIManager, UIMenu, UILabel

if TYPE_CHECKING:
    from ..core.game import Game

# (!) NO PROBADO
class WinState(GameState):
    """Estado de Win que se superpone al ganar la partida."""

    # (!) Intercambiar el final score por la Data para que muestre toda la info
    # (!) Si será como el de fnf entonces esto seria tipo un ResultsState
    # (!) Indiferentemente de eso, toca refactorizarla, esto es solo tentativo
    def __init__(self, game: "Game", final_score: int, song_folder: str):
        super().__init__(game)

        self.song_folder = song_folder

        font_title = self.game.resources.get_font("Cursive", 100)
        font_score = self.game.resources.get_font("Estandar", 48)
        font_menu = self.game.resources.get_font("Estandar", 48)

        options = [
            ("REINTENTAR", self._on_retry),
            ("VOLVER AL MENU", self._on_menu),
            ("SALIR", self._on_exit)
        ]

        screen_center_w = SCREEN_SIZE[0] // 2

        self.title = UILabel("game_title", screen_center_w, 150, "You win!", font_title, (255, 0, 0))
        self.score_text = UILabel("final_score", screen_center_w, 290, f"Rank: {final_score}", font_score)
        
        self.menu = UIMenu("game_over_menu", screen_center_w, 410,
                           options, font_menu, spacing=70, center_text=True)
        
        self.ui: UIManager = UIManager()
        self.ui.add_element(self.title)
        self.ui.add_element(self.score_text)
        self.ui.add_element(self.menu)
    
    def on_enter(self) -> None:
        # por si acaso
        self.game.audio.stop_all_sounds()  
    
    def on_exit(self) -> None:
        pass
    
    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "up"):
            self.menu.move_up()
        elif self.game.input.is_action_pressed("ui", "down"):
            self.menu.move_down()
        elif self.game.input.is_action_pressed("ui", "select"):
            self.menu.execute_selected()
    
    def update(self, dt: float) -> None:
        self.ui.update(dt)
    
    def render(self, surface: pygame.Surface) -> None:
        # Fondo semitransparente
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(200)
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
    def _on_exit(self):
        """Cierra la ventana del juego."""
        self.game._stop_context()
    
    def _on_retry(self):
        """Reinicia la partida."""
        self.game.state.clear()        
        self.game.state.change(StateID.PLAY, song_folder=self.song_folder)
    
    def _on_menu(self):
        """Vuelve al menú principal."""
        self.game.state.clear()
        self.game.state.change(StateID.MENU)