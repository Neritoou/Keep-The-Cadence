import pygame
from enum import Enum, auto
from typing import TYPE_CHECKING
from enfocate import SCREEN_SIZE

from .game_state import GameState
from .types import StateID, OverlayType
from ..ui import UIManager, UIMenu, UILabel
from ..ui import UICounterLabel
from ..core.scoring import MAX_STARS

if TYPE_CHECKING:
    from ..core.game import Game
    from ..states import PlayState
    from ..ui import UIElement

#  FASES

class _Phase(Enum):
    TITLE    = auto()
    STARS    = auto()
    COUNTERS = auto()
    RECORD   = auto()
    DONE     = auto()


# Duración de cada fase en ms
_PHASE_TITLE_MS  = 600
_PHASE_STARS_MS  = 800
_PHASE_RECORD_MS = 400

# Duración del fade de aparición en segundos
_FADE_DURATION         = 0.3
_FADE_COUNTER_DURATION = 0.2

# Layout
_CX        = 960   # centro columna derecha
_COL_LEFT  = 820   # Perfects / Bads
_COL_RIGHT = 1100  # Goods / Misses
_CHAR_X    = 320   # centro personaje
_CHAR_Y    = 360   # centro personaje


class WinState(GameState):
    """Estado de resultados al completar una canción."""

    def __init__(self, game: "Game", play_state: "PlayState"):
        super().__init__(game)
        self.play_state = play_state

        # --- Estrellas ---
        stars_sheet      = self.game.resources.get_spritesheet("Stars")
        self._base_star  = stars_sheet.get_frame_at(1, 0)
        self._full_star  = stars_sheet.get_frame_at(0, 0)
        self._reveal_stars = False

        # --- Guardar record ---
        record = self.play_state.score_manager.build_record()

        try:
            self._entered = self.game.database.save_record(
                self.play_state.song_id, self.play_state.diff, record
            )
        except ValueError as e:
            print(f"[WinState] Error al guardar record: {e}")
            self._entered = False

        self._record = record

        # --- Fuentes ---
        font_title = self.game.resources.get_font("Cursive",  100)
        font_menu  = self.game.resources.get_font("Estandar",  48)

        # --- Labels estáticos ---
        self._title        = UILabel("win_title",  _CX, 60,
                                     "YOU WIN!", font_title, (255, 215, 0))
        self._record_label = UILabel("win_record", _CX, 560,
                                     "¡NUEVO RECORD!" if self._entered else "",
                                     font_menu, (255, 80, 80), visible=False)

        # --- Contadores individuales ---
        self._c_score    = UICounterLabel("score",    _CX,        270, font_menu, fmt=lambda v: f"Score:     {int(v):,}")
        self._c_combo    = UICounterLabel("combo",    _CX,        330, font_menu, fmt=lambda v: f"Max combo: {int(v)}")
        self._c_perfects = UICounterLabel("perfects", _COL_LEFT,  390, font_menu, fmt=lambda v: f"Perfects: {int(v)}")
        self._c_goods    = UICounterLabel("goods",    _COL_RIGHT, 390, font_menu, fmt=lambda v: f"Goods: {int(v)}")
        self._c_bads     = UICounterLabel("bads",     _COL_LEFT,  450, font_menu, fmt=lambda v: f"Bads: {int(v)}")
        self._c_misses   = UICounterLabel("misses",   _COL_RIGHT, 450, font_menu, fmt=lambda v: f"Misses: {int(v)}")
        self._c_accuracy = UICounterLabel("accuracy", _CX,        498, font_menu, fmt=lambda v: f"Accuracy:  {v:.1f}%")

        # Contadores y targets juntos — evita desincronización por índice
        self._counter_queue: list[tuple[UICounterLabel, float]] = [
            (self._c_score,    float(record.points)),
            (self._c_combo,    float(record.max_combo)),
            (self._c_perfects, float(record.perfects)),
            (self._c_goods,    float(record.goods)),
            (self._c_bads,     float(record.bads)),
            (self._c_misses,   float(record.misses)),
            (self._c_accuracy, record.accuracy),

        ]
        self._counter_index = 0

        # --- Menú horizontal ---
        options = [
            ("REINTENTAR",     self._on_retry),
            ("VOLVER AL MENU", self._on_menu),
            ("SALIR",          self._on_exit),
        ]
        self._menu = UIMenu("win_menu", SCREEN_SIZE[0] // 2, 660,
                            options, font_menu, spacing=60, center_text=True)
        self._menu.visible = False

        # --- UIManager ---
        self._ui = UIManager()
        self._ui.add_element(self._title)
        self._ui.add_element(self._record_label)
        for counter, _ in self._counter_queue:
            self._ui.add_element(counter)
        self._ui.add_element(self._menu)

        # --- Estado de fases ---
        self._phase       = _Phase.TITLE
        self._phase_timer = 0.0
        self._menu_active = False

        # Título aparece con fade desde el inicio
        self._title.alpha = 0.0
        self._title.fade_to(255, _FADE_DURATION)

    def on_enter(self) -> None:
        self.game.audio.stop_all_sounds()
        self.game.character.set_position((_CHAR_X, _CHAR_Y))
        self.game.character.reset()
        self.game.character.play_win()

    def on_exit(self) -> None:
        pass

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if not self._menu_active:
            return
        if self.game.input.is_action_pressed("ui", "up"):
            self._menu.move_up()
        elif self.game.input.is_action_pressed("ui", "down"):
            self._menu.move_down()
        elif self.game.input.is_action_pressed("ui", "select"):
            self._menu.execute_selected()

    def update(self, dt: float) -> None:
        self.game.character.update(dt)
        self._ui.update(dt)
        self._advance(dt)

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(210)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        self.game.character.draw(surface)

        pygame.draw.line(surface, (60, 60, 60),
                         (SCREEN_SIZE[0] // 2, 40),
                         (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 80), 1)

        self._draw_stars(surface)
        self._ui.render(surface)

    #  FASES

    def _advance(self, dt: float) -> None:
        self._phase_timer += dt * 1000

        match self._phase:
            case _Phase.TITLE if self._phase_timer >= _PHASE_TITLE_MS:
                self._phase = _Phase.STARS
                self._phase_timer = 0.0

            case _Phase.STARS if self._phase_timer >= _PHASE_STARS_MS:
                self._phase = _Phase.COUNTERS
                self._phase_timer = 0.0
                self._start_counter(0)

            case _Phase.COUNTERS:
                self._advance_counters()

            case _Phase.RECORD if self._phase_timer >= _PHASE_RECORD_MS:
                self._phase = _Phase.DONE
                self._reveal_stars = True
                self._show(self._menu)
                self._menu_active = True

    def _advance_counters(self) -> None:
        counter, _ = self._counter_queue[self._counter_index]
        if counter.is_done:
            next_idx = self._counter_index + 1
            if next_idx < len(self._counter_queue):
                self._start_counter(next_idx)
            else:
                self._phase = _Phase.RECORD
                self._phase_timer = 0.0
                if self._entered:
                    self._show(self._record_label)

    def _start_counter(self, idx: int) -> None:
        self._counter_index = idx
        counter, target = self._counter_queue[idx]
        self._show(counter, fade_duration=_FADE_COUNTER_DURATION)
        counter.set_target(target)  

    def _draw_stars(self, surface: pygame.Surface) -> None:
        star_w  = self._base_star.get_width()
        padding = 10
        total_w = MAX_STARS * star_w + (MAX_STARS - 1) * padding
        start_x = _CX - total_w // 2
        y       = 180

        for i in range(MAX_STARS):
            frame = self._full_star if (self._reveal_stars and i < self._record.stars) else self._base_star
            surface.blit(frame, (start_x + i * (star_w + padding), y))


    def _show(self, element: "UIElement", fade_duration: float = _FADE_DURATION) -> None:
        element.visible = True
        element.alpha   = 0.0
        element.fade_to(255, fade_duration)


    def _on_exit(self) -> None:
        self.game._stop_context()

    def _on_retry(self) -> None:
        self.play_state.restart()
        self.game.state.exit_current()

    def _on_menu(self) -> None:
        self.game.state.clear()
        self.game.state.change(StateID.MENU)


    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.SEMITRANSPARENT

    @property
    def is_transient(self) -> bool:
        return False