from .types import Section
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame.font import Font
    from pygame import Surface

class NoteSectionEditor:
    """"""
    def __init__(self, song_duration: int):
        """
        Args:
            song_duration: duración de la canción (ms)
        """
        self.song_duration = song_duration
        self.sections: list[Section] = []
        self.current_index = 0
        
        
        self.visible_count = 10     # cuántas secciones se muestran
        self.scroll_offset = 0      # desde qué índice se dibuja

    def create(self, index: int, start: float, end: float | None = None) -> None:
        """Crea la primera sección (abierta)"""
        section = Section(
            index = index,
            start_time = start,
            end_time = end,  
            notes = []
        )
        self.sections.append(section)
    
    def can_close_current(self) -> bool:
        """Verifica si es posible cerrar la sección actual"""
        # Verificar si ya está cerrada
        if self.current.end_time is not None:
            return False
        return True
    
    def close_current(self, current_time: float) -> None:
        """Cierra la sección actual"""
        # Evita cerrar la sección después del final
        self.current.end_time = min(current_time, self.song_duration)

    def delete_current(self):
        """Elimina la sección actual (solo si es la última y está abierta)"""        
        
        # No se elimina si no es la última seccion
        if self.current_index != self.last_index:
            return
    
        # No permitir eliminar si es la única sección
        if self.sections_size == 1:
            return
        
        # Eliminar sección
        self.sections.pop()
        self.set_current_index(self.current_index - 1)
        
        # Reabrir la sección anterior
        self.current.end_time = None

    def set_current_index(self, index: int) -> None:
        """Establece el índice de la sección actual"""
        if not 0 <= index < self.sections_size:
            raise ValueError(
            f"NoteSectionEditor: Índice {index} fuera de rango. Válido: [0, {self.sections_size - 1}]"
        )
        self.current_index = index
        self._update_scroll()

    def next(self):
        """Mueve a la siguiente sección"""
        next_index = (self.current_index + 1) % self.sections_size
        self.set_current_index(next_index)

    def previous(self):
        """Mueve a la sección anterior"""
        prev_index = (self.current_index - 1) % self.sections_size
        self.set_current_index(prev_index)

    def _update_scroll(self):
        """
        Ajusta el scroll para que la sección actual siempre esté visible.
        Si hay menos secciones que `visible_count`, el scroll empieza en 0.
        """
        if self.sections_size <= self.visible_count:
            self.scroll_offset = 0
            return

        # Scroll mínimo para que la current_index esté visible
        scroll = self.current_index - self.visible_count + 1
        # Limitar scroll dentro del rango válido [0, sections_size - visible_count]
        self.scroll_offset = max(0, min(scroll, self.sections_size - self.visible_count))

    def move_to(self, index: int):
        """Salta a una sección específica"""
        if index > self.last_index or index < 0:
            raise ValueError(f"NoteSection: no es posible acceder al index {index}. Indices: [0/{self.last_index}]")
        self.set_current_index(index)

    def move_to_new(self):
        "Saltar automáticamente a la nueva sección"
        if not self.current.end_time:
            return
    
        self.create(self.sections_size, self.current.end_time)    
        # Moverse a la nueva sección
        self.set_current_index(self.last_index)

    def draw_list(self, surface: "Surface", font: "Font"):
        """Dibuja la lista de secciones"""
        x = 50
        y = 50
        
        title = font.render("SECCIONES", True, (255, 255, 255))
        surface.blit(title, (x, y))
        y += 30
        
        start = self.scroll_offset
        end = min(start + self.visible_count, self.sections_size)

        for index in range(start, end):
            section = self.sections[index]

            color = (0, 255, 0) if index == self.current_index else (200, 200, 200)

            end_time_str = f"{section.end_time/1000:.2f}s" if section.end_time else "???"
            status = "CERRADA" if section.end_time else "ABIERTA"
            notes_info = f"{len(section.notes)} notas" if section.notes else "VACÍA"

            section_info = (
                f"{section.index + 1}. "
                f"[{section.start_time/1000:.2f}s - {end_time_str}] "
                f"({notes_info}) {status}"
            )

            text = font.render(section_info, True, color)
            surface.blit(text, (x, y))
            y += 30

    @property
    def last_index(self) -> int:
        return len(self.sections) - 1
    
    @property
    def sections_size(self) -> int:
        return len(self.sections)
    
    @property
    def current(self) -> Section:
        return self.sections[self.current_index]