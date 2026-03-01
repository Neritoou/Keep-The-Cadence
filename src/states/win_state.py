import pygame
from enum import Enum, auto
from typing import TYPE_CHECKING
from enfocate import SCREEN_SIZE

from .game_state import GameState
from .types import StateID, OverlayType

from ..ui import UIManager, UILabel, UICounterLabel

from ..core.scoring import MAX_STARS
from ..util.conversors import get_hint_key

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
_COL_LEFT  = 650   # Perfects / Bads
_COL_RIGHT = 1000  # Goods / Misses
_CX        = 900   # centro columna derecha
_CHAR_X    = 320   # centro personaje
_CHAR_Y    = 340   # centro personaje

# Estética
BG_PANEL  = (18,  12,  38)   # azul marino
BD_PANEL  = (110, 80, 200)   # violeta

class WinState(GameState):
    """Estado de resultados al completar una canción."""

    def __init__(self, game: "Game", play_state: "PlayState"):
        super().__init__(game)
        self.play_state = play_state

        self.w, self.h = SCREEN_SIZE

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

        # --- Estado de fases ---
        self._phase       = _Phase.TITLE
        self._phase_timer = 0.0
        self._hint_active = False

        self._build_fonts()
        self._build_ui()
        self._build_static_surfaces()

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
        if not self._hint_active:
            return
        if self.game.input.is_action_pressed("ui", "select"):
            self._on_menu()    

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

        self._draw_stars(surface)
        self._ui.render(surface)

        # Barra de hints
        if self._hint_active:
            self._draw_hint_bar(surface)

    def _draw_hint_bar(self, surface: pygame.Surface) -> None:
        bar_y = self.h - 50
        surface.blit(self._hint_bar, (0, bar_y))

        # Centrar todos los hints en la barra
        gap = 38
        total_w = sum(p.get_width() + k.get_width() + a.get_width() for p, k, a in self._hint_renders)
        total_w += gap * (len(self._hint_renders) - 1)

        cur_x = (self.w - total_w) // 2
        text_y = bar_y + 8

        for p_surf, k_surf, a_surf in self._hint_renders:
            surface.blit(p_surf, (cur_x, text_y))
            cur_x += p_surf.get_width()
            surface.blit(k_surf, (cur_x, text_y))
            cur_x += k_surf.get_width()
            surface.blit(a_surf, (cur_x, text_y))
            cur_x += a_surf.get_width() + gap

    def _draw_stars(self, surface: pygame.Surface) -> None:
        star_w  = self._base_star.get_width()
        padding = 10
        total_w = MAX_STARS * star_w + (MAX_STARS - 1) * padding
        start_x = _CX - total_w // 2
        y       = 190

        for i in range(MAX_STARS):
            frame = self._full_star if (self._reveal_stars and i < self._record.stars) else self._base_star
            surface.blit(frame, (start_x + i * (star_w + padding), y))

    def _build_hints(self) -> list[tuple[str, str]]:
        k = self.game.controls_config
        return [
            (get_hint_key(k,"select"),"para seleccionar otra canción.")
        ]
    
    def _build_fonts(self) -> None:
        self._fonts = {
            "title": self.game.resources.get_font("Cursive",  100),
            "record": self.game.resources.get_font("Estandar",  48),
            "menu": self.game.resources.get_font("Estandar",  45),
            "small": self.game.resources.get_font("Alternative", 35)
        }

    def _build_static_surfaces(self) -> None:
        """Pre-genera superficies que no cambian frame a frame."""

        self._hint_bar = pygame.Surface((self.w, 50), pygame.SRCALPHA)
        self._hint_bar.fill((8, 4, 18))

        self._hint_renders: list[tuple[pygame.Surface, pygame.Surface, pygame.Surface]] = []
        for key_str, action_str in self._build_hints():
            p = self._fonts["small"].render(f"Presiona", True, (150, 135, 190))
            k = self._fonts["small"].render(f" [{key_str}]", True, (190, 165, 255))
            a = self._fonts["small"].render(f" {action_str}", True, (150, 135, 190))
            self._hint_renders.append((p, k, a))

    def _build_ui(self) -> None:
        # --- Labels estáticos ---
        self._title        = UILabel("win_title",  _CX, 50,
                                     "Ganaste!", self._fonts["title"], (255, 215, 0))
        self._notes        = UILabel("win_title",  _CX, 440,
                                     "----- Conteo de Notas -----", self._fonts["menu"], (255, 255, 255),
                                     visible=False)
        self._record_label = UILabel("win_record", _CX, 610,
                                     "¡NUEVO RECORD!" if self._entered else "",
                                     self._fonts["record"], (255, 80, 80), visible=False)

        # --- Contadores individuales ---
        self._c_score    = UICounterLabel("score",    _CX,  270, self._fonts["menu"], fmt=lambda v: f"Puntuación: {int(v):,}", center=True)
        self._c_combo    = UICounterLabel("combo",    _CX,  320, self._fonts["menu"], fmt=lambda v: f"Max combo:  {int(v)}", center=True)
        self._c_accuracy = UICounterLabel("accuracy", _CX,  370, self._fonts["menu"], fmt=lambda v: f"Precisión:  {v:.1f}%", center=True)
        self._c_perfects = UICounterLabel("perfects", _COL_LEFT,  490, self._fonts["menu"], fmt=lambda v: f"Perfectas: {int(v)}")
        self._c_goods    = UICounterLabel("goods",    _COL_RIGHT, 490, self._fonts["menu"], fmt=lambda v: f"Buenas: {int(v)}")
        self._c_bads     = UICounterLabel("bads",     _COL_LEFT,  540, self._fonts["menu"], fmt=lambda v: f"Malas: {int(v)}")
        self._c_misses   = UICounterLabel("misses",   _COL_RIGHT, 540, self._fonts["menu"], fmt=lambda v: f"Fallos: {int(v)}")

        # Contadores y targets juntos — evita desincronización por índice
        self._counter_queue: list[tuple[UICounterLabel, float]] = [
            (self._c_score,    float(self._record.points)),
            (self._c_combo,    float(self._record.max_combo)),
            (self._c_accuracy, self._record.accuracy),
            (self._c_perfects, float(self._record.perfects)),
            (self._c_goods,    float(self._record.goods)),
            (self._c_bads,     float(self._record.bads)),
            (self._c_misses,   float(self._record.misses)),
        ]
        self._counter_index = 0

        # --- UIManager ---
        self._ui = UIManager()
        self._ui.add_element(self._title)
        self._ui.add_element(self._notes)
        self._ui.add_element(self._record_label)
        for counter, _ in self._counter_queue:
            self._ui.add_element(counter)

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
                self._hint_active = True

    def _advance_counters(self) -> None:
        counter, _ = self._counter_queue[self._counter_index]
        if counter.is_done:
            next_idx = self._counter_index + 1
            if next_idx < len(self._counter_queue):
                self._start_counter(next_idx)

                if next_idx == len(self._counter_queue) // 2:
                    self._show(self._notes)
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

    def _show(self, element: "UIElement", fade_duration: float = _FADE_DURATION) -> None:
        element.visible = True
        element.alpha   = 0.0
        element.fade_to(255, fade_duration)

    def _on_menu(self) -> None:
        self.game.state.clear()
        self.game.state.change(StateID.SONG_SELECT)


    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.SEMITRANSPARENT

    @property
    def is_transient(self) -> bool:
        return False