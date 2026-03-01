import pygame
from typing import TYPE_CHECKING
from enfocate import SCREEN_SIZE

from .game_state import GameState
from .types import StateID, OverlayType

from ..core.database import DifficultyName, Song, Difficulty, Record
from ..util.paths import get_inst_path
from ..util.conversors import get_hint_key
from ..ui import UIManager, UISlideMenu, UILabel, UISongDetailPanel

if TYPE_CHECKING:
    from ..core.game import Game

PREVIEW_DELAY_MS    = 300       # ms de espera antes de arrancar el preview
PREVIEW_START_SEC   = 30.0      # segundo desde el que empieza
PREVIEW_DURATION_MS = 30_000    # duración del fragmento en ms (30 s)

DIFF_ORDER = [DifficultyName.EASY, DifficultyName.NORMAL, DifficultyName.HARD]

# Estética
BG_PANEL  = (18,  12,  38, 210)   # azul marino
BD_PANEL  = (110, 80, 200, 160)   # violeta


class SongSelectState(GameState):
    """Estado de selección de canción."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)

        self._songs      = self.game.database.songs
        self._song_index = 0
        self._diff_index = 1

        self._preview_delay_ms   = 0.0   # acumula ms hasta arrancar el preview
        self._preview_elapsed_ms = 0.0   # acumula ms desde que el preview está sonando
        self._preview_active     = False

        # Dimensiones de la pantalla
        self.w, self.h = SCREEN_SIZE

        self.stars: list[pygame.Surface]  = [
            pygame.transform.smoothscale(
                self.game.resources.get_spritesheet("Stars").get_frame_at(row, 0, trim=True),
                (30, 30)
            )
            for row in range(2)
        ]

        # Caché de superficies pre-calculadas para evitar recrearlas cada frame
        self._diff_pill_cache: dict[DifficultyName, pygame.Surface] = {}

        self._build_fonts()
        self._build_static_surfaces()
        self._build_ui()

    def on_enter(self) -> None:
        self._reset_preview()

    def on_exit(self) -> None:
        self.game.audio.stop_all_sounds()

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "up"):
            self.game.audio.play_sfx("scroll")
            self.songs_menu.move_up()
            self._move_song(-1)
            
        elif self.game.input.is_action_pressed("ui", "down"):
            self.game.audio.play_sfx("scroll")
            self.songs_menu.move_down()
            self._move_song(1)

        elif self.game.input.is_action_pressed("ui", "left"):
            self.game.audio.play_sfx("scroll")
            self._move_diff(-1)

        elif self.game.input.is_action_pressed("ui", "right"):
            self.game.audio.play_sfx("scroll")
            self._move_diff(1)

        elif self.game.input.is_action_pressed("ui", "select"):
            self.game.audio.play_sfx("select")
            self._try_start_game()

        elif self.game.input.is_action_pressed("ui", "back"):
            self.game.state.change_with_transition(StateID.MENU)

    def update(self, dt: float) -> None:
        self.count_str.set_text(f"{self._song_index + 1} / {len(self._songs)}")

        current_diff = self._get_current_diff()
        records = current_diff.records if current_diff else []
        
        self.detail_panel.set_data(
            song=self._get_current_song(),
            diff_name=self._get_current_diff_name(),
            records=records
        )

        self._ui.update(dt)
        self._update_preview(dt * 1000)

    def _update_preview(self, dt_ms: float) -> None:
        if not self._preview_active:
            # Esperar el delay inicial antes de arrancar
            self._preview_delay_ms += dt_ms
            if self._preview_delay_ms >= PREVIEW_DELAY_MS:
                self._start_preview()
        else:
            # Contar cuánto lleva sonando el fragmento
            self._preview_elapsed_ms += dt_ms
            if self._preview_elapsed_ms >= PREVIEW_DURATION_MS:
                self._restart_preview()

    def render(self, surface: pygame.Surface) -> None:
        # Fondo
        surface.blit(self.bg, (0,0))

        self._ui.render(surface)

        # Barra de hints
        self._draw_hint_bar(surface)

    def _draw_hint_bar(self, surface: pygame.Surface) -> None:
        bar_y = self.h - 50
        surface.blit(self._hint_bar, (0, bar_y))

        # Centrar todos los hints en la barra
        gap = 38
        total_w = sum(k.get_width() + a.get_width() for k, a in self._hint_renders)
        total_w += gap * (len(self._hint_renders) - 1)

        cur_x = (self.w - total_w) // 2
        text_y = bar_y + 8

        for k_surf, a_surf in self._hint_renders:
            surface.blit(k_surf, (cur_x, text_y))
            cur_x += k_surf.get_width()
            surface.blit(a_surf, (cur_x, text_y))
            cur_x += a_surf.get_width() + gap



    # --- Métodos privados ---
        #  --- Datos de las canciones ---
    def _get_songs(self) -> list[Song]:
        """Lista completa de canciones."""
        return self._songs

    def _get_current_song(self) -> Song:
        """Canción seleccionada actualmente."""
        return self._songs[self._song_index]

    def _get_current_song_index(self) -> int:
        """Índice de la canción seleccionada."""
        return self._song_index

        #  --- Datos de las dificultad ---
    def _get_diff_order(self) -> list[DifficultyName]:
        """Orden de dificultades disponibles."""
        return DIFF_ORDER

    def _get_current_diff_name(self) -> DifficultyName:
        """Nombre de la dificultad activa."""
        return DIFF_ORDER[self._diff_index]

    def _get_current_diff(self) -> Difficulty | None:
        """Objeto Difficulty activo, o None si no existe."""
        return self._get_current_song().get_difficulty(self._get_current_diff_name())

        # --- Datos del record ---
    def _get_current_records(self) -> list[Record]:
        """Records de la dificultad activa. Lista vacía si no hay ninguno."""
        diff = self._get_current_diff()
        return diff.records if diff else []

    def _get_top_record(self) -> Record | None:
        """Record #1 de la dificultad activa, o None."""
        diff = self._get_current_diff()
        return diff.top_record if diff else None

        #  --- Navegación ---
    def _move_song(self, direction: int) -> None:
        self._song_index = (self._song_index + direction) % len(self._songs)
        self._reset_preview()

    def _move_diff(self, direction: int) -> None:
        self._diff_index = (self._diff_index + direction) % len(DIFF_ORDER)

    def _try_start_game(self) -> None:
        diff = self._get_current_diff()

        if diff is None:
            return
        
        song = self._get_current_song()
        self.game.audio.stop_music()   # fade antes de cambiar de estado
        self.game.state.change_with_transition(
            StateID.PLAY,
            song_folder=song.name,
            song_id=song.id,
            difficulty=self._get_current_diff_name(),
        )

        # --- PREVIEW DE AUDIO ---
    def _reset_preview(self) -> None:
        """Para el audio y reinicia todos los contadores."""
        self.game.audio.stop_music()
        self._preview_delay_ms   = 0.0
        self._preview_elapsed_ms = 0.0
        self._preview_active     = False

    def _start_preview(self) -> None:
        """Arranca el fragmento desde PREVIEW_START_SEC."""
        try:
            path = str(get_inst_path(self._get_current_song().name))
            self.game.audio.play_music(path, loops=-1, start=PREVIEW_START_SEC, fade_ms=500)
            self._preview_active     = True
            self._preview_elapsed_ms = 0.0
        except FileNotFoundError:
            self._preview_active = True  # No reintentar

    def _restart_preview(self) -> None:
        """Vuelve al segundo 30 sin detener la música (sin corte audible)."""
        self._preview_elapsed_ms = 0.0
        pygame.mixer.music.set_pos(PREVIEW_START_SEC)

        # --- Construcción de la UI y superficies ---
    def _build_fonts(self) -> None:
        self.fonts = {
            "title": self.game.resources.get_font("Alternative", 90),
            "song": self.game.resources.get_font("Alternative", 48),
            "button": self.game.resources.get_font("Estandar", 48),
            "medium": self.game.resources.get_font("Alternative", 42),
            "small": self.game.resources.get_font("Alternative", 35)
        }
    
    def _build_static_surfaces(self) -> None:
        """Pre-genera superficies que no cambian frame a frame."""
        self.bg = self.game.resources.get_image("Background2")

        self._hint_bar = pygame.Surface((self.w, 50), pygame.SRCALPHA)
        self._hint_bar.fill((8, 4, 18, 200))

        pygame.draw.line(self._hint_bar, BD_PANEL, (0, 0), (self.w, 0), 1)

        self._hint_renders: list[tuple[pygame.Surface, pygame.Surface]] = []
        for key_str, action_str in self._build_hints():
            k = self.fonts["small"].render(f"[{key_str}]", True, (190, 165, 255))
            a = self.fonts["small"].render(f" {action_str}", True, (150, 135, 190))
            self._hint_renders.append((k, a))

    def _build_ui(self) -> None:
        """Construye todos los elementos de la UI."""

        # Título y Contador
        self.title = UILabel("select_title", 60, 40, "Lista de Canciones", self.fonts["title"], (60, 40, 40), center=False)
        self.count_str = UILabel("song_count", 90, 130, "1 / X", self.fonts["small"], (60, 40, 40), center=False)

        # Menú deslizable de canciones
        song_options = [
            (song.name, lambda _i=i: None)
            for i, song in enumerate(self._songs)
        ]

        btn_surface = pygame.Surface((600, 80), pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, (213, 176, 191), btn_surface.get_rect(), border_radius=45)

        sel_surface = pygame.Surface((600, 80), pygame.SRCALPHA)
        pygame.draw.rect(sel_surface, (213, 176, 191), sel_surface.get_rect(), border_radius=45)
        pygame.draw.rect(sel_surface, (60, 40, 40), sel_surface.get_rect(), width=5, border_radius=45)

        icon = self.game.resources.get_image("Record")
        menu_icons: list[pygame.Surface] = []

        for song in song_options:
            menu_icons.append(icon)

        self.songs_menu = UISlideMenu(
            "songs_menu", 520, 180, song_options, btn_surface, self.fonts["button"],
            (60, 40, 40), selected_surface=sel_surface, content_padding=30,
            spacing=15, hidden_offset=110, icons=menu_icons, show_selected_icon=True
        )

        # Sprites de estrellas para el panel (evitamos cargarlas de nuevo dentro del panel)
        stars_spritesheet = self.game.resources.get_spritesheet("Stars")
        stars_sprites = [
            pygame.transform.smoothscale(
                stars_spritesheet.get_frame_at(row, 0, trim=True), (30, 30)
            ) for row in range(2)
        ]

        self.detail_panel = UISongDetailPanel(
            "song_detail_panel", 590, 150, 640, 480, self.fonts,
            stars_sprites, BG_PANEL, BD_PANEL
        )

        # Manager
        self._ui = UIManager()
        self._ui.add_element(self.title)
        self._ui.add_element(self.count_str)
        self._ui.add_element(self.songs_menu)
        self._ui.add_element(self.detail_panel)
    
    def _build_hints(self) -> list[tuple[str, str]]:
        k = self.game.controls_config
        return [
            (f"{get_hint_key(k,'up')} / {get_hint_key(k,'down')}",    "Cancion"),
            (f"{get_hint_key(k,'left')} / {get_hint_key(k,'right')}", "Dificultad"),
            (get_hint_key(k,"select"),"Jugar"),
            (get_hint_key(k,"back"),"Volver"),
        ]
    
    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE

    @property
    def is_transient(self) -> bool:
        return False