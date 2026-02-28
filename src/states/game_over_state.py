import pygame
from enum import Enum, auto
from typing import TYPE_CHECKING
from enfocate import SCREEN_SIZE

from .game_state import GameState
from .types import StateID, OverlayType
from ..ui import UIManager, UIMenu, UILabel
from ..constants import MIKU_PLAY_POSITION

if TYPE_CHECKING:
    from ..core.game import Game
    from ..states import PlayState
    from ..core.types import NoteDirection

# --- Timings ---
_ZOOM_DURATION_MS = 1000.0  # Duración del zoom hacia Miku en ms
_HOLD_DURATION_MS = 600.0   # Tiempo de espera en zoom máximo antes de mostrar el UI
_FADE_DURATION    = 0.5     # Duración del fade in de los elementos UI en segundos
_ZOOM_TARGET      = 0.50    # Fracción de pantalla que ocupa la región al final del zoom (0.5 = 50%)

class _Phase(Enum):
    """Fases internas del estado de Game Over."""
    ZOOM = auto()   # Acercamiento progresivo a la cara de Miku
    HOLD = auto()   # Zoom fijo, pausa dramática antes de mostrar el UI
    UI   = auto()   # Overlay oscuro visible con menú y puntuación

class GameOverState(GameState):
    """
    Estado de Game Over que se superpone al PlayState al perder la partida.

    Reproduce una secuencia de tres fases:
        1. ZOOM: zoom in progresivo hacia la cara de Miku con ease out.
        2. HOLD: pausa con zoom fijo para efecto dramático.
        3. UI: aparece el overlay oscuro con título, puntuación y menú con fade in.
    """
    def __init__(self, game: "Game", play_state: "PlayState", direction: "NoteDirection"):
        super().__init__(game)
        self.play_state = play_state
        self._final_direction = direction

        self._phase       = _Phase.ZOOM
        self._phase_timer = 0.0   # Acumulador de tiempo en ms para la fase actual
        self._menu_active = False # True cuando el fade terminó y el menú acepta input

        # Punto de enfoque del zoom: ligeramente arriba del centro del personaje (cara)
        mx, my = MIKU_PLAY_POSITION
        self._focus = (mx, my - 80)

        # --- Fuentes ---
        font_title = self.game.resources.get_font("Cursive", 100)
        font_score = self.game.resources.get_font("Estandar", 48)
        font_menu  = self.game.resources.get_font("Estandar", 48)

        cx = SCREEN_SIZE[0] // 2

        options = [
            ("REINTENTAR",     self._on_retry),
            ("VOLVER AL MENU", self._on_menu),
            ("SALIR",          self._on_exit),
        ]

        # --- UI: se crea oculta y se revela con fade en fase UI ---
        self.title      = UILabel("game_title",    cx, 150, "Game Over :(", font_title, (255, 0, 0), visible=False, alpha=0)
        self.score_text = UILabel("final_score",   cx, 290, f"Puntuacion final: {self.play_state.score_manager.score}", font_score, visible=False, alpha=0)
        self.menu       = UIMenu("game_over_menu", cx, 410, options, font_menu, spacing=70, center_text=True, visible=False, alpha=0)

        self.ui = UIManager()
        self.ui.add_element(self.title)
        self.ui.add_element(self.score_text)
        self.ui.add_element(self.menu)

        # Surface donde se escribe el zoom cada frame.
        self._zoomed_surface = pygame.Surface(SCREEN_SIZE)

        # Overlay negro semitransparente.
        self._overlay = pygame.Surface(SCREEN_SIZE)
        self._overlay.set_alpha(200)
        self._overlay.fill((0, 0, 0))

    def on_enter(self) -> None:
        self.game.audio.stop_music()
        self.game.audio.stop_all_sounds()
        self.game.character.press_miss(self._final_direction)
        self.game.character.animator.go_to_frame(len(self.game.character.animator.frames) - 1)

    def on_exit(self) -> None:
        pass

    # --- INPUT ---
    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if not self._menu_active:
            return
        if self.game.input.is_action_pressed("ui", "up"):
            self.menu.move_up()
        elif self.game.input.is_action_pressed("ui", "down"):
            self.menu.move_down()
        elif self.game.input.is_action_pressed("ui", "select"):
            self.menu.execute_selected()

    # --- UPDATE ---
    def update(self, dt: float) -> None:
        self._phase_timer += dt * 1000

        match self._phase:
            case _Phase.ZOOM:
                if self._phase_timer >= _ZOOM_DURATION_MS:
                    self._phase = _Phase.HOLD
                    self._phase_timer = 0.0

            case _Phase.HOLD:
                if self._phase_timer >= _HOLD_DURATION_MS:
                    self._phase = _Phase.UI
                    self._phase_timer = 0.0
                    # Revelar UI con fade in
                    for element in (self.title, self.score_text):
                        element.visible = True
                        element.fade_to(255, _FADE_DURATION)
                    self.menu.visible = True
                    self.menu.fade_to_all(255, _FADE_DURATION)

            case _Phase.UI:
                self.ui.update(dt)
                # Activar menú una vez que el fade del título terminó
                if not self._menu_active and not self.title.is_fading:
                    self._menu_active = True

    # --- RENDER ---
    def render(self, surface: pygame.Surface) -> None:
        """
        Renderiza según la fase actual:
        - ZOOM/HOLD: actualiza y dibuja el zoom progresivo sobre la escena del PlayState.
        - UI: dibuja el zoom congelado + overlay oscuro + elementos de UI.
        """
        if self._phase != _Phase.UI:
            self._render_zoom(surface)
        
        surface.blit(self._zoomed_surface, (0, 0))
        
        if self._phase == _Phase.UI:
            surface.blit(self._overlay, (0, 0))
            self.ui.render(surface)

    def _render_zoom(self, surface: pygame.Surface) -> None:
        """
        Calcula la región de zoom y la escala a pantalla completa usando smoothscale,
        escribiendo el resultado directo en _zoomed_surface para evitar allocations.

        El progreso usa ease out cuadrático: rápido al inicio, suave al final.
        En fase HOLD el progreso se fija en 1.0 para mantener el zoom máximo.
        """
        w, h = surface.get_size()
        progress = min(self._phase_timer / _ZOOM_DURATION_MS, 1.0) if self._phase == _Phase.ZOOM else 1.0
        t = 1.0 - (1.0 - progress) ** 2 # ease out cuadrático

        # Región que se recorta: empieza en pantalla completa y se reduce hasta ZOOM_TARGET
        zoom_w = int(w * (1.0 - (1.0 - _ZOOM_TARGET) * t))
        zoom_h = int(h * (1.0 - (1.0 - _ZOOM_TARGET) * t))

        # Centrar la región en el punto de enfoque, clampeado a los bordes
        fx, fy = self._focus
        x = max(0, min(fx - zoom_w // 2, w - zoom_w))
        y = max(0, min(fy - zoom_h // 2, h - zoom_h))

        try:
            region = surface.subsurface(pygame.Rect(x, y, zoom_w, zoom_h))
            pygame.transform.smoothscale(region, (w, h), self._zoomed_surface)
        except ValueError:
            pass

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.SEMITRANSPARENT

    @property
    def is_transient(self) -> bool:
        return False

    # --- CALLBACKS ---
    def _on_exit(self):
        self.game._stop_context()

    def _on_retry(self):
        self.game.state.exit_current()
        self.play_state.restart()

    def _on_menu(self):
        self.game.state.clear()
        self.game.state.change(StateID.MENU)