import pygame
from typing import TYPE_CHECKING

from .game_state import GameState
from .types import StateID, OverlayType
from ..database import DifficultyName, Song, Difficulty, Record
from ..util.paths import get_inst_path

if TYPE_CHECKING:
    from ..core.game import Game

DIFF_ORDER = [DifficultyName.EASY, DifficultyName.NORMAL, DifficultyName.HARD]

PREVIEW_DELAY_MS    = 300       # ms de espera antes de arrancar el preview
PREVIEW_START_SEC   = 30.0      # segundo desde el que empieza
PREVIEW_DURATION_MS = 30_000    # duración del fragmento en ms (30 s)


class SongSelectState(GameState):

    def __init__(self, game: "Game") -> None:
        super().__init__(game)

        self._songs      = self.game.database.songs
        self._song_index = 0
        self._diff_index = 0

        self._preview_delay_ms   = 0.0   # acumula ms hasta arrancar el preview
        self._preview_elapsed_ms = 0.0   # acumula ms desde que el preview está sonando
        self._preview_active     = False

    def on_enter(self) -> None:
        self._reset_preview()

    def on_exit(self) -> None:
        self.game.audio.stop_all_sounds()

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self.game.input.is_action_pressed("ui", "up"):
            self._move_song(-1)
        elif self.game.input.is_action_pressed("ui", "down"):
            self._move_song(1)
        elif self.game.input.is_action_pressed("ui", "pause"):
            self.game.state.change_with_transition(StateID.MENU)
        elif self.game.input.is_key_pressed(pygame.K_LEFT):
            self._move_diff(-1)
        elif self.game.input.is_key_pressed(pygame.K_RIGHT):
            self._move_diff(1)
        elif self.game.input.is_action_pressed("ui", "select"):
            self._try_start_game()

    def update(self, dt: float) -> None:
        dt_ms = dt * 1000

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
        surface.fill((0, 0, 0))
        w, h = surface.get_size()
        font_big   = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 30)

        # Lista de canciones
        for i, song in enumerate(self._songs):
            color  = (255, 255, 255) if i == self._song_index else (120, 120, 120)
            prefix = "> " if i == self._song_index else "  "
            surface.blit(font_big.render(f"{prefix}{song.name}", True, color), (40, 80 + i * 50))

        # Dificultad seleccionada
        diff_name = self.get_current_diff_name()
        surface.blit(font_big.render(f"< {diff_name.value} >", True, (100, 180, 255)), (w // 2 + 20, 80))

        # Records
        records = self.get_current_records()
        y = 160
        if not records:
            surface.blit(font_small.render("Sin records", True, (80, 80, 80)), (w // 2 + 20, y))
        for rank, rec in enumerate(records, 1):
            stars = "★" * rec.stars + "☆" * (4 - rec.stars)
            surface.blit(font_small.render(f"#{rank} {stars}  {rec.points:,} pts  {rec.date}", True, (200, 200, 200)), (w // 2 + 20, y))
            y += 35

    #  DATOS — CANCIONES
    def get_songs(self) -> list[Song]:
        """Lista completa de canciones."""
        return self._songs

    def get_current_song(self) -> Song:
        """Canción seleccionada actualmente."""
        return self._songs[self._song_index]

    def get_current_song_index(self) -> int:
        """Índice de la canción seleccionada."""
        return self._song_index

    #  DATOS — DIFICULTAD
    def get_diff_order(self) -> list[DifficultyName]:
        """Orden de dificultades disponibles."""
        return DIFF_ORDER

    def get_current_diff_name(self) -> DifficultyName:
        """Nombre de la dificultad activa."""
        return DIFF_ORDER[self._diff_index]

    def get_current_diff(self) -> Difficulty | None:
        """Objeto Difficulty activo, o None si no existe."""
        return self.get_current_song().get_difficulty(self.get_current_diff_name())

    #  DATOS — RECORDS
    def get_current_records(self) -> list[Record]:
        """Records de la dificultad activa. Lista vacía si no hay ninguno."""
        diff = self.get_current_diff()
        return diff.records if diff else []

    def get_top_record(self) -> Record | None:
        """Record #1 de la dificultad activa, o None."""
        diff = self.get_current_diff()
        return diff.top_record if diff else None

    #  NAVEGACIÓN
    def _move_song(self, direction: int) -> None:
        self._song_index = (self._song_index + direction) % len(self._songs)
        self._reset_preview()

    def _move_diff(self, direction: int) -> None:
        self._diff_index = (self._diff_index + direction) % len(DIFF_ORDER)

    def _try_start_game(self) -> None:
        diff = self.get_current_diff()
        if diff is None:
            return
        song = self.get_current_song()
        self.game.audio.stop_music()   # fade antes de cambiar de estado
        self.game.state.change_with_transition(
            StateID.PLAY,
            song_folder=song.name,
            song_id=song.id,
            difficulty=self.get_current_diff_name(),
        )

    #  PREVIEW DE AUDIO
    def _reset_preview(self) -> None:
        """Para el audio y reinicia todos los contadores."""
        self.game.audio.stop_music()
        self._preview_delay_ms   = 0.0
        self._preview_elapsed_ms = 0.0
        self._preview_active     = False

    def _start_preview(self) -> None:
        """Arranca el fragmento desde PREVIEW_START_SEC."""
        try:
            path = str(get_inst_path(self.get_current_song().name))
            self.game.audio.play_music(path, loops=-1, start=PREVIEW_START_SEC, fade_ms=500)
            self._preview_active     = True
            self._preview_elapsed_ms = 0.0
        except FileNotFoundError:
            self._preview_active = True  # No reintentar

    def _restart_preview(self) -> None:
        """Vuelve al segundo 30 sin detener la música (sin corte audible)."""
        self._preview_elapsed_ms = 0.0
        pygame.mixer.music.set_pos(PREVIEW_START_SEC)

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE

    @property
    def is_transient(self) -> bool:
        return False