from pygame import Surface, Rect
from typing import TYPE_CHECKING
from ...resources import Animation
from ..receptor_state import ReceptorFSM, NoteReceptorState

if TYPE_CHECKING:
    from .note import Note
    from ..types import NoteDataType, NoteDirection, ScrollDirection

class NoteRenderer:
    """
    Clase que permite dibujar las notas de una sección.
    Maneja tanto notas TAP como HOLD, con scroll configurable.
    """
    def __init__(self, notes_data: "NoteDataType", hit_line_xs: tuple[int,...],
                 hit_line_y: int, scroll_direction: "ScrollDirection", 
                 spawn_time_ms: float, miss_display_ms: float, screen_height: int
                ):
        """
        Args:
            notes_data: Diccionario con superficies y partículas por dirección.
            hit_line_xs: Posiciones X de cada lane (una por dirección).
            hit_line_y: Posición Y de la línea de hit.
            scroll_direction: Dirección en la que se mueven las notas (UP o DOWN).
            spawn_time_ms: Tiempo de anticipación del spawn respecto al hit (ms).
            screen_height: Alto de la pantalla, usado para cálculos de visibilidad.
        """
        self.notes_data = notes_data
        self.hit_line_xs = list(hit_line_xs)  # lista para permitir modificación
        self.hit_line_y = hit_line_y
        self.scroll_direction = scroll_direction
        self.screen_height = screen_height
        self.spawn_time_ms = spawn_time_ms
        self._miss_display_ms = miss_display_ms
        
        # Una FSM por dirección para controlar el estado visual del receptor
        self.receptors: "dict[NoteDirection, ReceptorFSM]" = {
            direction: ReceptorFSM(state=NoteReceptorState.IDLE)

            for direction in notes_data.keys()
        }

       # Una animación por dirección (static / confirm / miss)
        self.receptor_animations: "dict[NoteDirection, Animation]" = {
            direction: self._build_animation(direction)
            for direction in notes_data.keys()
        }

    def reset_receptors(self) -> None:
        """Resetea todos los receptores a estado IDLE."""
        for direction in self.receptors:
            self.receptors[direction].state = NoteReceptorState.IDLE
            self.receptors[direction].direction = None
            self.receptors[direction].timer = 0.0

    # --- INPUT ---
    def press_hit(self, direction: "NoteDirection") -> None:
        """Notifica al receptor que se presionó una tecla con hit correcto."""
        fsm = self.receptors[direction]
        fsm.state = NoteReceptorState.HOLD_HIT
        fsm.timer = 0.0

    def press_miss(self, direction: "NoteDirection") -> None:
        """Notifica al receptor que se presionó una tecla con miss."""
        fsm = self.receptors[direction]
        fsm.state = NoteReceptorState.HOLD_MISS
        fsm.timer = 0.0  # ← resetear timer al entrar en miss

    def release_key(self, direction: "NoteDirection") -> None:
        """Notifica al receptor que se soltó una tecla."""
        fsm = self.receptors[direction]
        match fsm.state:
            case NoteReceptorState.HOLD_HIT:
                fsm.state = NoteReceptorState.RELEASE_HIT
            case NoteReceptorState.HOLD_MISS:
                fsm.state = NoteReceptorState.RELEASE_MISS
            # En cualquier otro estado no hay transición al soltar

    # --- SETTERS DE POSICIONES DE LAS NOTAS ---
    def set_hit_line_y(self, y: int) -> None:
        """Cambia la posición Y de la línea de hit."""
        self.hit_line_y = y

    def set_hit_line_x(self, direction: "NoteDirection", x: int) -> None:
        """Cambia la posición X de un lane específico."""
        self.hit_line_xs[direction] = x

    def set_hit_line_xs(self, xs: tuple[int, int, int, int]) -> None:
        """Reemplaza todas las posiciones X de los lanes."""
        self.hit_line_xs = list(xs)

    def offset_hit_line_xs(self, offset_x: int) -> None:
        """Desplaza horizontalmente todos los lanes por un valor."""
        self.hit_line_xs = [x + offset_x for x in self.hit_line_xs]

    # --- UPDATE ---
    def update(self, dt: float) -> None:
        """Actualiza la FSM y la animación de cada receptor."""
        for direction, fsm in self.receptors.items():
            anim = self.receptor_animations[direction]
            match fsm.state:
                case NoteReceptorState.IDLE:
                    self._update_idle(anim, dt)
                case NoteReceptorState.HOLD_HIT:
                    self._update_hold_hit(anim)
                case NoteReceptorState.HOLD_MISS:
                    self._update_hold_miss(anim, dt)
                case NoteReceptorState.RELEASE_HIT:
                    self._update_release_hit(direction, anim, dt)
                case NoteReceptorState.RELEASE_MISS:
                    self._update_release_miss(direction, anim, dt)

    def _update_idle(self, anim: Animation, dt: float) -> None:
        """IDLE: Muestra imagen static"""
        if anim.get_current_animation_name() != "static":
            anim.play("static", reset=True, loop=True)

        anim.update(dt)

    def _update_hold_hit(self, anim: Animation) -> None:
        """HOLD_HIT: Congela el primer frame de confirm mientras se mantiene la tecla"""
        if anim.get_current_animation_name() != "confirm":
            anim.play("confirm", reset=True, loop=False)

        anim.go_to_frame(0)
        anim.pause()

    def _update_hold_miss(self, anim: Animation, dt: float) -> None:
        """HOLD_MISS: Muestra imagen miss estática mientras se mantiene la tecla"""
        if anim.get_current_animation_name() != "miss":
            anim.play("miss", reset=True, loop=False)
        anim.update(dt)

    def _update_release_hit(self, direction: "NoteDirection", anim: Animation, dt: float) -> None:
        """RELEASE_HIT: Reproduce confirm desde donde quedó congelado hasta el final"""
        if anim.get_current_animation_name() != "confirm":
            anim.play("confirm", reset=True, loop=False)

        anim.resume()
        anim.update(dt)

        # Al terminar la animación vuelve a IDLE
        if anim.is_last_frame() and not anim.is_playing():
            self._go_idle(direction)

    def _update_release_miss(self, direction: "NoteDirection", anim: Animation, dt: float) -> None:
        """RELEASE_MISS: Vuelve a static inmediatamente"""
        fsm = self.receptors[direction]
        if anim.get_current_animation_name() != "miss":
            anim.play("miss", reset=True, loop=False)
        anim.update(dt)
        fsm.timer += dt
        if fsm.timer >= self._miss_display_ms:
            self._go_idle(direction)

    def _go_idle(self, direction: "NoteDirection") -> None:
        fsm = self.receptors[direction]
        fsm.state = NoteReceptorState.IDLE
        fsm.direction = None
        fsm.timer = 0.0


    # --- DIBUJAR NOTAS ---
    def draw_receptors(self, surface):
        """Dibuja los receptores animados sobre la hit line."""
        for direction, anim in self.receptor_animations.items():
            x = self.hit_line_xs[direction]
            anim.draw_centered(surface, (x, self.hit_line_y))

    def draw_notes(self, surface: Surface, notes: "list[Note]", current_time: float, pixels_per_ms: float) -> None:
        """Dibuja todas las notas visibles de una sección"""
        for note in notes:
            if not note.is_visible(current_time, self.spawn_time_ms):
                continue
            if note.is_hold_note:
                self._draw_hold_note(surface, note, current_time, pixels_per_ms)
            else:
                self._draw_tap_note(surface, note, current_time, pixels_per_ms)

    def _draw_tap_note(self, surface: Surface, note: "Note", 
                      current_time: float, pixel_per_ms: float) -> None:
        """Dibuja una nota TAP en su posición Y interpolada."""
        delta = note.hit_time - current_time
        y_head = int(self.hit_line_y - delta * pixel_per_ms * self.scroll_direction.value)
        x = self.hit_line_xs[note.direction]
        
        note_surface = self.notes_data[note.direction]["surfaces"]["spawned"]
        note_rect = note_surface.get_rect(center=(x, y_head))
        
        surface.blit(note_surface, note_rect)

    def _draw_hold_note(self, surface: Surface, note: "Note", current_time: float, pixels_per_ms: float) -> None:
        """
        Dibuja una nota HOLD con cabeza, cuerpo y cola.

        Si la nota ya fue golpeada (current_time >= hit_time), la cabeza
        se ancla a la hit line y el cuerpo se acorta según el tiempo restante.
        """
        x = self.hit_line_xs[note.direction]
        
        # Calcular posición de la head
        if current_time < note.hit_time:
            # Nota aún no golpeada 
            delta = note.hit_time - current_time
            y_head = int(self.hit_line_y - delta * pixels_per_ms * self.scroll_direction.value)
            remaining_duration = max(note.duration, 0.0)
        else:
            # Nota ya golpeada: cabeza anclada en la hit line
            y_head = self.hit_line_y
            remaining_duration = max(note.end_time - current_time, 0)

        # Calcular largo de la nota en píxeles
        note_length = int(remaining_duration * pixels_per_ms)

        if note_length <= 0:
            # Sin duración restante, dibujar solo la cabeza como TAP
            self._draw_tap_note(surface, note, current_time, pixels_per_ms)
            return

        # Calcular posición de la cola
        y_tail = y_head - note_length * self.scroll_direction.value

        # Acceso directo a las Surfaces
        # Orden de dibujado: cuerpo → cola → cabeza (la cabeza siempre encima)
        data = self.notes_data[note.direction]["surfaces"]
        head_surface = data["spawned"]
        body_surface = data["hold"]
        tail_surface = data["end_hold"]

        # Dibujar el cuerpo
        self._tile_hold_body(surface, body_surface, x, y_head, y_tail)

        # Dibujar cola
        tail_rect = tail_surface.get_rect(center=(x, y_tail))
        surface.blit(tail_surface, tail_rect)

        # Dibujar la cabeza encima de todo
        head_rect = head_surface.get_rect(center=(x, y_head))
        surface.blit(head_surface, head_rect)

    def _tile_hold_body(self, surface: Surface, body_surface: Surface,
                        x: int, y_head: int, y_tail: int) -> None:
        """
        Rellena el cuerpo de una nota HOLD repitiendo el sprite verticalmente (tiling).

        Se dibuja de y_start (menor Y) a y_end (mayor Y) para que funcione
        tanto en scroll UP como DOWN sin invertir el sprite.
        """
        body_w, body_h = body_surface.get_width(), body_surface.get_height()

        # Calcular rango a llenar (siempre de menor a mayor en pantalla)
        y_start = min(y_head, y_tail)
        y_end = max(y_head, y_tail)
        total_length = y_end - y_start

        if total_length <= 0:
            return

        # Cuántos tiles completos
        num_full_tiles = total_length // body_h
        remaining_pixels = total_length % body_h

        # Posición X centrada
        x_offset = x - body_w // 2
        y = y_start

        # Dibujar tiles completos
        for _ in range(num_full_tiles):
            surface.blit(body_surface, (x_offset, y))
            y += body_h

        # Tile parcial: se recorta el sprite para no sobrepasar el largo exacto
        if remaining_pixels > 0:
            try:
                clipped = body_surface.subsurface(Rect(0, 0, body_w, remaining_pixels))
                surface.blit(clipped, (x_offset, y))
            except ValueError:
                pass
    
    # --- HELPERS ---
    def _build_animation(self, direction: "NoteDirection") -> Animation:
        """Construye la animación del receptor para una dirección."""
        surfaces = self.notes_data[direction]["surfaces"]

        # Normaliza a lista por si alguna superficie viene como Surface suelta
        def to_list(s):
            return s if isinstance(s, list) else [s]

        return Animation(
            animations={
                "static":  to_list(surfaces["default"]),
                "confirm": surfaces["pressed"], # ya viene como lista de frames
                "miss":    to_list(surfaces["missed"]),
            },
            default="static",
            base_fps=12,
            fps_map={"static": 1, "confirm": 12, "miss": 1},
            loop=True
        )
    
    def draw_default_notes(self, surface: Surface) -> None:
        """
        Dibuja las notas default en la pantalla.
        Método auxiliar para el Chart Editor
        """
        for direction, data in self.notes_data.items():
            note_surface = data["surfaces"]["default"]
            rect = note_surface.get_rect(center = (self.hit_line_xs[direction], self.hit_line_y))
            surface.blit(note_surface, rect)