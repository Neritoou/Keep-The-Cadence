from typing import TYPE_CHECKING, Callable
from random import choice

from ..types import NoteDirection, Judgement
from .note import Note
from ..types import NoteState
from ..scoring import ScoreManager
from ...constants import HOLD_END_WINDOW_MS, INPUT_OFFSET_MS

if TYPE_CHECKING:
    from .note_renderer import NoteRenderer
    from ..character import Character
    from ..chart_player import ChartPlayer

class NoteInputHandler:
    """
    Procesa el input del jugador y lo traduce en eventos de juego.

    Attributes:
        player: Referencia al ChartPlayer para leer el tiempo actual y las notas activas.
        renderer: Renderer de notas para actualizar el estado visual de los receptores.
        character: Personaje jugable para disparar animaciones de hit/miss.
    """
    def __init__(
            self, player: "ChartPlayer", renderer: "NoteRenderer", 
            character: "Character",
            score_manager: ScoreManager
            ):
        """
        Args:
            player: ChartPlayer en curso.
            renderer: NoteRenderer.
            character: Personaje jugable.
            miss_sounds: Sonidos de fallo — se elige uno al azar en cada miss.
        """
        self.player    = player
        self.renderer  = renderer
        self.character = character
        self._miss_sounds: list[str] = [f"miss_note_{i}" for i in range(1, 4)]
        self._on_judgement: Callable[[Judgement], None] | None = None

        # Holds que el jugador está sosteniendo activamente (ACTIVE)
        self._held_notes:   "dict[NoteDirection, Note | None]" = {d: None for d in NoteDirection}

        # Holds que se perdieron (sin presionar o drop) pero siguen
        # visibles en pantalla hasta que llegan a su end_time
        self._missed_holds: "dict[NoteDirection, Note | None]" = {d: None for d in NoteDirection}

        self._score = score_manager

    # --- INPUT PÚBLICO ---
    def on_key_press(self, direction: "NoteDirection") -> None:
        """
        Punto de entrada para un press de tecla del jugador.

        Busca la nota PENDING más cercana en la dirección dada. Si existe,
        la procesa como hit; si no, como ghost press.
        """
        note = self._find_hittable_note(direction)
        if note is None:
            self._handle_ghost_press(direction)
        else:
            self._handle_hit(note, direction)

    def on_key_release(self, direction: "NoteDirection") -> None:
        """
        Punto de entrada para un release de tecla del jugador.

        Si había una hold activa en esa dirección, evalúa si el jugador
        la soltó dentro del window final (completada) o antes (drop).
        Si no había hold activa, solo libera el estado visual.
        """
        note = self._held_notes[direction]

        if note is None:
            # Sin hold activa: solo liberar visual.
            # release_key en el renderer solo transiciona si está en HOLD_HIT,
            # así no interrumpe animaciones de miss en curso
            self.renderer.release_key(direction)
            self.character.release_key(direction)
            return
        
        time_remaining = note.end_time - self.player.real_time

        if time_remaining > HOLD_END_WINDOW_MS:
            self._handle_hold_drop(note, direction)
        else:
            self._handle_hold_complete(note, direction)
                                       
    def update(self, dt: float) -> None:
        """
        Actualiza el estado de holds y procesa misses automáticos.

        Debe llamarse cada frame DESPUÉS de ChartPlayer.update() para
        garantizar que _active_notes esté al día antes de evaluarlas.
        """
        self._update_hold_tracking()

        for note in self.player.pop_missed_notes():
            print(f"[MISS AUTO] {note.direction.name} | hold: {note.is_hold_note}")
            self.renderer.press_miss(note.direction)
            self.character.press_miss(note.direction)
            self.player.mute_voices()
            self._play_miss_sound()

            self._score.register_tap(Judgement.MISS)

            if self._on_judgement:
                self._on_judgement(Judgement.MISS)

            if note.is_hold_note:
                # La hold sigue visible hasta su end_time para mostrar cuánto faltaba
                self._missed_holds[note.direction] = note
            else:
                # Tap: transicionar a RELEASE_MISS para que la animación
                # se reproduzca y vuelva a idle sola por timer
                self.renderer.release_key(note.direction)
                self.character.release_key(note.direction)


  

    def _handle_hit(self, note: "Note", direction: "NoteDirection") -> None:
        """
        Procesa un press exitoso sobre una nota hittable.

        Calcula el judgement, avanza el estado de la nota y notifica
        al renderer, personaje y audio. Si es hold, la registra en
        _held_notes para tracking posterior.
        """
        judgement = note.get_judgement(self.player.real_time + INPUT_OFFSET_MS,self.player.diff_data.judgement_windows)
        note.on_hit()  # PENDING -> ACTIVE (hold) | PENDING -> COMPLETED (tap)
        
        self._score.register_tap(judgement)

        if self._on_judgement:
            self._on_judgement(judgement)

        self.renderer.press_hit(direction)
        self.character.press_hit(direction)
        self.player.unmute_voices()

        if note.is_hold_note:
            self._held_notes[direction] = note

        # TODO: enviar judgement al sistema de Score
        print(f"[HIT] {direction.name} — {judgement.name} | hold: {note.is_hold_note}")

    def _handle_ghost_press(self, direction: "NoteDirection") -> None:
        """
        Procesa un press sin nota hittable cercana.

        No mutea las voices porque no había nota que perder.
        El renderer y el personaje quedan en HOLD_MISS hasta que el
        jugador suelte la tecla, momento en que on_key_release los libera.
        """
        self.renderer.press_miss(direction)
        self.character.press_miss(direction)
        self._play_miss_sound()
        self._score.register_ghost_press()

        if self._on_judgement:
            self._on_judgement(Judgement.MISS)
        
        print(f"[GHOST] {direction.name}")
        
    def _handle_hold_drop(self, note: "Note", direction: "NoteDirection") -> None:
        """
        Procesa un drop de hold: el jugador soltó demasiado pronto.

        La nota pasa a MISSED pero se mantiene en _missed_holds para
        seguir renderizándose hasta su end_time.

        Args:
            note: Hold activa que se está dropeando.
            direction: Dirección de la hold.
        """
        judgement = note.get_judgement(self.player.real_time + INPUT_OFFSET_MS,self.player.diff_data.judgement_windows)
        note.on_missed()  # ACTIVE -> MISSED
        self._score.register_ghost_press()

        if self._on_judgement:
            self._on_judgement(judgement)

        self._held_notes[direction]   = None
        self._missed_holds[direction] = note  # sigue visible hasta end_time

        self.renderer.press_miss(direction)
        self.character.press_miss(direction)
        self.player.mute_voices()
        self._play_miss_sound()

        # TODO: enviar judgement al sistema de Score como hold drop
        print(f"[DROP] {direction.name} — {judgement.name}")

    def _handle_hold_complete(self, note: "Note", direction: "NoteDirection") -> None:
        """
        Procesa una hold completada: el jugador soltó dentro del window final.

        Args:
            note: Hold activa que se completó.
            direction: Dirección de la hold.
        """
        note.on_completed()  # ACTIVE -> COMPLETED

        self._score.register_hold_release(1.0)

        self._held_notes[direction] = None
        self.character.release_key(direction)
        self.renderer.release_key(direction)
        print(f"[HOLD COMPLETA] {direction.name}")


    # --- LÓGICA DE NOTAS ---
    def _find_hittable_note(self, direction: "NoteDirection") -> "Note | None":
        """
        Busca la nota PENDING más cercana al hit_time en la dirección dada.

        Solo considera notas en estado PENDING — las ACTIVE, COMPLETED y
        MISSED no son golpeables.        
        """
        current_time = self.player.real_time + INPUT_OFFSET_MS
        best: "Note | None" = None
        best_delta = float("inf")

        for note in self.player.current_notes:
            if note.direction != direction:
                continue
            if note.state != NoteState.PENDING:  # solo PENDING es golpeable
                continue
            if not note.is_hittable(current_time, self.player.diff_data.judgement_windows):
                continue
            delta = abs(note.hit_time - current_time)
            if delta < best_delta:
                best, best_delta = note, delta

        return best

    def _update_hold_tracking(self) -> None:
        """
        Libera automáticamente las holds cuando llegan a su end_time.

        Holds activas (bien presionadas): se completan y disparan on_hold_complete.
        Holds falladas (miss o drop): solo se limpian visualmente.
        """        
        current_time = self.player.real_time

        for direction in NoteDirection:
            # Hold activa: el jugador la sostuvo hasta el final
            note = self._held_notes[direction]

            if note is not None and current_time >= note.end_time:
                note.on_completed()  # ACTIVE -> COMPLETED
                self._score.register_hold_release(1.0)

                self._held_notes[direction] = None
                self.renderer.release_key(direction)
                self.character.release_key(direction)

            # Hold fallada: terminó su tiempo de display, limpiar visual
            note = self._missed_holds[direction]
            if note is not None and current_time >= note.end_time:
                self._missed_holds[direction] = None
                self.renderer.release_key(direction)
                self.character.release_key(direction)

    def _play_miss_sound(self) -> None:
        """Reproduce un sonido de fallo aleatorio de entre los disponibles."""
        sound = choice(self._miss_sounds)
        self.player.audio.play_sfx(sound)

    def reset(self) -> None:
        """Limpia las holds activas y fallidas."""
        self._held_notes   = {d: None for d in NoteDirection}
        self._missed_holds = {d: None for d in NoteDirection}