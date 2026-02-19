import pygame
import json
from typing import TYPE_CHECKING
from .music_editor_controller import MusicEditorController
from .note_editor_controller import NoteEditorController
from .note_section_editor import NoteSectionEditor
from ..note_renderer import NoteRenderer
from .chart_editor_ui import ChartEditorUI
from ..types import NoteDirection
from .types import EditorKeyState, EditorInfo

if TYPE_CHECKING:
    from ..types import ScrollDirection, JsonChartData, JsonSectionData
    from ..types import NoteDataType

class ChartEditor:
    """Editor de charts"""
    def __init__(self, song_path: str, song_name: str, bpm: int, chart_path: str, hit_line_y: int, 
                 hit_line_xs: tuple[int,int,int,int], scroll_direction: "ScrollDirection",
                 base_pixels_per_ms: float, spawn_time_ms: float, notes_data: "NoteDataType"):
        
        # Config Base
        self.notes_data = notes_data
        self.song_name = song_name
        self.song_path = song_path
        self.chart_path = chart_path
        self.bpm = bpm
        self.scroll_direction = scroll_direction
        self.base_pixels_per_ms = base_pixels_per_ms

        # (!) Pantalla, posiblemente se elimina
        self.screen_width = 1280
        self.screen_height = 720

        # Timing
        self.ms_per_beat = 60000 / self.bpm
        self.ms_per_step = self.ms_per_beat / 4  # 16th notes
        
        # Datos de las Notas
        self.hit_line_y = hit_line_y
        self.hit_line_xs = hit_line_xs

        # Componentes
        self.music = MusicEditorController(self.song_path, base_pixels_per_ms)
        self.song_duration = self.music.get_song_length()

        self.note_section = NoteSectionEditor(self.song_duration)
        self.note_controller = NoteEditorController(self.song_duration, self.ms_per_step)

        self.ui = ChartEditorUI(self.screen_width, self.screen_height)

        self.note_renderer = NoteRenderer(notes_data,
                                          hit_line_xs,
                                          hit_line_y,
                                          scroll_direction,
                                          spawn_time_ms,
                                          self.screen_height
        )

        # Estado de teclas
        self.key_states: dict[NoteDirection, EditorKeyState] = {
            NoteDirection.UP: EditorKeyState(),
            NoteDirection.LEFT: EditorKeyState(),
            NoteDirection.DOWN: EditorKeyState(),
            NoteDirection.RIGHT: EditorKeyState()
        }

        self._spawn_time_ms = spawn_time_ms
        self._update_spawn_time_ms()
        # Crear primera sección
        self.note_section.create(0, 0.0)


    # --- CÁLCULO DEL SPAWN DE LAS NOTAS ---
    def _update_spawn_time_ms(self) -> None:
        """Recalcula el spawn time basándose en pixels_per_ms actual"""
        # Determinar la posición inicial de la nota fuera de pantalla
        if self.scroll_direction.value == 1:  # Downscroll
            spawn_y = -50 
        else:  # Upscroll
            spawn_y = self.screen_height + 50  

        # Distancia que debe recorrer la nota hasta la hit line
        distance_px = abs(self.hit_line_y - spawn_y)

        # Tiempo en ms que tarda en recorrer esa distancia
        self._spawn_time_ms = distance_px / self.music.pixels_per_ms
    
    @property
    def spawn_time_ms(self) -> float:
        """Tiempo de anticipación del spawn (ms)"""
        return self._spawn_time_ms


    # --- VELOCIDAD DE LAS NOTAS ---
    def add_pixel_per_ms(self) -> None:
        """Incrementa velocidad en 0.01 px/ms"""
        self.music.pixels_per_ms += 0.01
        self._update_spawn_time_ms()  
    
    def remove_pixel_per_ms(self) -> None:
        """Decrementa velocidad en 0.01 px/ms"""
        self.music.pixels_per_ms -= 0.01
        self._update_spawn_time_ms() 


    # --- PLAYBACK ---
    def toggle_play_pause(self) -> None:
        """Alterna play/pause"""
        self.music.toggle_play_pause()
    
    def toggle_loop(self) -> None:
        """Alterna modo loop"""
        self.music.toggle_loop()

    def toggle_snap(self) -> None:
        """Alterna snap to grid"""
        self.note_controller.toggle_snap()

    @property
    def is_playing(self) -> bool:
        """¿Está reproduciendo?"""
        return self.music.playing
    
    
    # --- SECCIONES ---
    def close_section(self) -> None:
        """Cierra sección actual"""
        if self.note_section.can_close_current():
            self.note_section.close_current(self.music.current_time)
            self.note_section.move_to_new()
            self.jump_to_current_section()
    
    def delete_section(self) -> None:
        """Elimina sección actual"""
        self.note_section.delete_current()
        self.jump_to_current_section()
    
    def next_section(self) -> None:
        """Va a siguiente sección"""
        self.note_section.next()
        self.jump_to_current_section()
    
    def previous_section(self) -> None:
        """Va a sección anterior"""
        self.note_section.previous()
        self.jump_to_current_section()
    
    def jump_to_section(self, index: int) -> None:
        """Salta a sección específica"""
        try:
            self.note_section.move_to(index)
            self.jump_to_current_section()
        except ValueError:
            pass
    
    def jump_to_current_section(self) -> None:
        """Salta al inicio de la sección actual"""
        self.music.stop()
        self.music.play(self.note_section.current.start_time)
        


    # --- INPUT DE LAS NOTAS ---
    def on_key_press(self, direction: NoteDirection) -> None:
        """Maneja cuando se presiona una tecla."""
        if not self.music.playing:
            return
        
        if self.note_section.current.end_time is not None:
            return
            
        key_state = self.key_states[direction]
  
        # Si ya está presionada, ignorar (evitar re-triggers)
        if key_state.is_pressed:
            return
        self.note_renderer.press_hit(direction)
        # Marcar como presionada y guardar tiempo
        key_state.is_pressed = True
        key_state.press_start_time = self.music.current_time
        key_state.is_hold_note = False


    
    def on_key_hold(self, direction: NoteDirection) -> None:
        """ Maneja cuando se mantiene una tecla. """
        key_state = self.key_states[direction]
        
        # Solo marcar como hold si está presionada
        if not key_state.is_pressed or key_state.is_hold_note:
            return
        
        # Marcar que será una hold note
        key_state.is_hold_note = True
    
    def on_key_release(self, direction: NoteDirection) -> None:
        """Maneja cuando se suelta una tecla y crea la nota correspondiente."""
        key_state = self.key_states[direction]
        
        # Si no estaba presionada, ignorar
        if not key_state.is_pressed:
            return
        
        if key_state.press_start_time >= self.song_duration:
            key_state.reset()
            return
        
        self.note_renderer.release_key(direction)
        # Calcular duración
        duration = 0.0
        if key_state.is_hold_note:
            duration = max(self.music.current_time - key_state.press_start_time, 0.0)

        # Crear nota
        note = self.note_controller.place_note(
            self.note_section.current,
            direction, 
            key_state.press_start_time,
            duration
        ) 

        # Log
        note_type = "HOLD" if note.is_hold_note else "TAP"
        duration_str = f"{note.duration:.0f}ms" if note.is_hold_note else ""
        print(f"Nota {note_type} creada: {direction.name} @ {note.hit_time:.0f}ms {duration_str}")

        # Resetear estado
        key_state.reset()

    def remove_last_note(self) -> None:
        """Elimina la última nota y limpia estados"""
        if not self.note_controller.can_remove_last_note(self.note_section.current):
            return
        
        removed = self.note_controller.remove_last_note(self.note_section.current)
        # Limpiar estado de tecla si estaba activa
        direction = NoteDirection(removed.direction)
        self.key_states[direction].reset()
            
        print(f"Nota eliminada: {direction.name}")

    def update(self,dt: float) -> None:
        """Actualiza el editor cada frame"""
        self.music.update()
        # Actualizar estados
        self.note_renderer.update(dt)
        current = self.note_section.current
        
        # Si Sección abierta alcanzó fin de canción
        if current.end_time is None:
            if self.music.has_reached(self.song_duration):
                self._handle_song_end()
                return
        
        # Si Sección cerrada alcanzó su fin
        if current.end_time is not None:
            if self.music.has_reached(current.end_time):
                self._handle_section_end()

        
    def _handle_song_end(self) -> None:
        """Maneja cuando se alcanza el fin de la canción"""
        self.note_section.close_current(self.song_duration)
        
        if self.note_section.sections_size > 1:
            self.note_section.next()
            self.jump_to_current_section()
        else:
            self.music.pause()
    
    def _handle_section_end(self) -> None:
        """Maneja cuando se alcanza el fin de una sección"""
        if self.music.loop_enabled:
            self.jump_to_current_section()  # Reiniciar misma sección
        else:
            self.note_section.next()  # Siguiente sección
            self.jump_to_current_section()


    def render(self, surface: pygame.Surface) -> None:
        """Renderiza todo"""
        surface.fill((30, 30, 30))
        # Notas
        if self.note_section.current.end_time is not None:
            self.note_renderer.draw_default_notes(surface) 
            self.note_renderer.draw_notes(
                surface,
                self.note_section.current.notes,
                self.music.current_time, 
                self.music.pixels_per_ms)
        else:
            self.note_renderer.draw_receptors(surface)
        # UI
        self.note_section.draw_list(surface, self.ui.font_small)
                
        info = EditorInfo(
            bpm=self.bpm,
            current_time = self.music.current_time,
            song_duration = self.song_duration,
            section_index = self.note_section.current_index,
            total_sections = self.note_section.sections_size,
            section_status = "ABIERTA" if self.note_section.current.end_time is None else "CERRADA",
            notes_count = len(self.note_section.current.notes),
            music_playing = self.music.playing,
            snap_enabled = self.note_controller.snap_enabled,
            loop_enabled = self.music.loop_enabled,
            can_export = self.can_export_to_json(),
            pixels_per_ms = self.music.pixels_per_ms
        )
        
        self.ui.draw_info(surface, info,self._spawn_time_ms)
        self.ui.draw_controls(surface)
        
        if not self.music.playing:
            self.ui.draw_paused_overlay(surface)
    
    def can_export_to_json(self) -> bool:
        """Retorna True si todas las secciones están cerradas"""
        return all(section.end_time is not None for section in self.note_section.sections)
    
    def export_to_json(self) -> None:
        """
        Exporta el chart a formato JSON.
            
        Args:
            output_path: Path donde guardar el JSON
        """
        if not self.can_export_to_json():
            return
            
        # Construir datos del chart
        chart_data: "JsonChartData" = {
            "song": self.song_name,
            "bpm": self.bpm,
            "pixels_per_ms": self.music.pixels_per_ms,
            "sections": []
        }
            
        for section in self.note_section.sections:
            # Validar que todas las secciones estén cerradas
            if section.end_time is None:
                raise ValueError(
                    f"ChartEditor: No se puede exportar la Data. Sección {section.index + 1} no está cerrada"
                )
                
            # Construir datos de la sección
            section_data: "JsonSectionData" = {
                "index": section.index,
                "startTime": section.start_time,
                "endTime": section.end_time,
                "notes": [
                    {
                        "hitTime": note.hit_time, 
                        "duration": note.duration,
                        "direction": note.direction
                    }
                    for note in section.notes
                ]
            }

            chart_data["sections"].append(section_data)
            
        # Guardar a archivo
        with open(self.chart_path, 'w', encoding='utf-8') as f:
            json.dump(chart_data, f, indent=2, ensure_ascii=False)