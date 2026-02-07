from pygame import Surface, draw
from typing import TYPE_CHECKING
from .types import ScrollDirection

if TYPE_CHECKING:
    from .note import Note

class NoteRenderer:
    """
    Clase que permite dibujar notas en el editor de charts o en el gameplay.
    Maneja tanto notas TAP como HOLD, con scroll configurable.
    """
    def __init__(self, hit_line_xs: tuple[int,int,int,int], lane_colors: list[tuple],
                 hit_line_y: int, scroll_direction: ScrollDirection, 
                 spawn_time_ms: float, screen_height: int
                ):
        """
        Args:
            hit_line_xs: Posiciones X de cada lane
            lane_colors: Colores RGB de cada lane
            hit_line_y: Posición Y de la línea de hit
            ms_per_step: Milisegundos por step (escala temporal)
            pixel_per_step: Pixeles por step (escala visual)
            scroll_direction: Dirección de scroll de las notas
            note_radius: Radio de las notas en píxeles
        """
        self.hit_line_xs = hit_line_xs
        self.hit_line_y = hit_line_y
        self.scroll_direction = scroll_direction
        self.screen_height = screen_height
        self.spawn_time_ms = spawn_time_ms

        # (!) ELIMINAR
        self.note_radius = 20
        self.lane_colors = lane_colors
    
    def draw_notes(self, surface: Surface, notes: "list[Note]", current_time: float, pixel_per_ms: float) -> None:
        """Dibuja todas las notas visibles de una sección"""
        for note in notes:
            self._draw_single_note(surface, note, current_time, pixel_per_ms)

    def _draw_single_note(self, surface: Surface, note: "Note", current_time: float, pixel_per_ms: float) -> None:
        """Dibuja una nota individual (tap o hold)"""
        if not note.is_visible(current_time, self.spawn_time_ms):
            return
        
        delta = note.hit_time - current_time

        y_head = self.hit_line_y - delta * pixel_per_ms * self.scroll_direction.value
        x = self.hit_line_xs[note.direction]

        color = self.lane_colors[note.direction]

        if note.is_hold_note:
            # Duración restante en píxeles
            remaining_pixels = max(note.duration, 0) * pixel_per_ms

            # Si ya pasó el hit_time, solo dibuja lo que queda
            if current_time >= note.hit_time:
                remaining_pixels = max(note.end_time - current_time, 0) * pixel_per_ms
                y_head = self.hit_line_y

            # Duración restante en píxeles 
            y_tail = y_head - remaining_pixels * self.scroll_direction.value

            # Dibujar la cola de la nota
            draw.line(surface,color,(x, y_head),(x, int(y_tail)),self.note_radius * 2)

        # Dibujar la cabeza de la nota
        draw.circle(surface, color, (x, y_head), self.note_radius)
        draw.circle(surface, (255, 255, 255), (x, y_head), self.note_radius, 2)


    
    def draw_hit_line(self, surface: Surface,
                      start_x: int = 350, end_x: int = 900,
                      color: tuple = (255, 255, 0), thickness: int = 3) -> None:

        """Dibuja la línea de hit en la pantalla"""
        draw.line(surface, color, (start_x, self.hit_line_y), (end_x, self.hit_line_y), thickness)