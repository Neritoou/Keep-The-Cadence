import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import EditorInfo

# (!) CAMBBIAR POR UI MANAGER
class ChartEditorUI:
    """Maneja toda la UI del editor de charts"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.info_pos = (950, 50)
        self._controls_pos = (50, self.screen_height - 300)

        # Fuentes
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
    
    def draw_info(self, surface: pygame.Surface, info: "EditorInfo",note_spawn_time: float) -> None:
        """Dibuja la información del estado"""
        x, y = self.info_pos
        
        progress_percent = (info.current_time / info.song_duration) * 100
        playback_status = "REPRODUCIENDO" if info.music_playing else "PAUSADO"
        playback_color = (0, 255, 0) if info.music_playing else (255, 255, 0)
        
        info_lines = [
            f"BPM: {info.bpm}",
            f"Tiempo: {info.current_time / 1000:.2f}s / {info.song_duration/1000:.2f}s",
            f"Progreso: {progress_percent:.1f}%",
            f"Sección: {info.section_index + 1}/{info.total_sections} ({info.section_status})",
            f"Notas: {info.notes_count}",
            "",
        ]
        
        for line in info_lines:
            text = self.font_small.render(line, True, (255, 255, 255))
            surface.blit(text, (x, y))
            y += 30
        
        # Estado de reproducción
        status_text = self.font_small.render(playback_status, True, playback_color)
        surface.blit(status_text, (x, y))
        y += 30
        
        # Configuración
        other_lines = [
            f"Can Export: {'YES' if info.can_export else 'NO'}",
            f"Snap: {'ON' if info.snap_enabled else 'OFF'}",
            f"Loop: {'ON' if info.loop_enabled else 'OFF'}",
            f"Pixels x MS: {info.pixels_per_ms}",
            f"Time to Hit: {note_spawn_time:.2f}ms"
        ]
        
        for line in other_lines:
            text = self.font_small.render(line, True, (255, 255, 255))
            surface.blit(text, (x, y))
            y += 30
 
    def draw_controls(self, surface: pygame.Surface) -> None:
        """Dibuja los controles disponibles"""
        x, y = self._controls_pos
        
        title = self.font_medium.render("CONTROLES", True, (255, 255, 255))
        surface.blit(title, (x, y))
        y += 35
        
        controls = [
            "SPACE: Play/Pause",
            "ENTER: Cerrar sección actual",
            "DEL: Eliminar sección vacía",
            "L: Toggle Loop sección",
            "UP/DOWN: Navegar secciones",
            "W/A/S/D: Colocar notas",
            "BACKSPACE: Eliminar última nota",
            "LEFT/RIGHT: Modificar Note Scroll Speed",
            "N: Toggle snap",
            "ESC: Exportar y salir"
        ]
        
        for control in controls:
            text = self.font_small.render(control, True, (200, 200, 200))
            surface.blit(text, (x, y))
            y += 25
    
    def draw_paused_overlay(self, surface: pygame.Surface) -> None:
        """Dibuja el overlay de pausa"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSADO", True, (255, 255, 0))
        text_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        surface.blit(pause_text, text_rect)
        
        instruction = self.font_medium.render("Presiona SPACE para continuar", True, (200, 200, 200))
        inst_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 60))
        surface.blit(instruction, inst_rect)