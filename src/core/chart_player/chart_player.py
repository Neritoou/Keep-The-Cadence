import pygame
from typing import TYPE_CHECKING

from .chart_data import LoadedChart
from ..note import Note

if TYPE_CHECKING:
    from ...audio import AudioManager

class ChartPlayer:
    """
    Controla la reproducción de un chart con sincronización de audio.
    
    Responsabilidades:
    - Sincronizar tiempo del chart con la música
    - Proporcionar notas visibles en cada momento
    - Controlar play/pause/stop
    """
    
    def __init__(self, chart: LoadedChart, audio_manager: "AudioManager", 
                 music_path: str, spawn_time_ms: float):
        """
        Args:
            chart: Chart ya cargado.
            audio_manager: Gestor de audio del juego.
            music_path: Ruta al archivo de música.
            spawn_time_ms: Tiempo de anticipación para spawn de notas.
        """
        self.chart = chart
        self.audio = audio_manager
        self.music_path = music_path
        self.spawn_time_ms = spawn_time_ms
        
        # Estado de reproducción
        self._playing = False
        self.current_time = 0.0
        self._start_tick = 0
        
        # Cache de notas activas
        self._active_notes: list[Note] = []
        self._last_cache_time = -1.0

    @property
    def is_playing(self) -> bool:
        """Verifica si está reproduciéndose."""
        return self._playing
    
    @property
    def is_finished(self) -> bool:
        """Verifica si el chart terminó."""
        return self.current_time >= self.chart.total_duration



    # --- CONTROL DE REPRODUCCIÓN ---
    def play(self, start_time: float = 0.0) -> None:
        """
        Inicia la reproducción del chart desde un tiempo específico.
        Siempre recarga el audio desde esa posición.
        """
        self.audio.play_music(self.music_path, 0, start_time / 1000)
        
        self.current_time = start_time
        self._start_tick = pygame.time.get_ticks() - int(start_time)
        self._playing = True
        
        print(f"ChartPlayer: Reproducción iniciada desde {start_time:.0f}ms")
    
    def pause(self) -> None:
        """Pausa la reproducción."""
        if not self._playing:
            return
        
        self.audio.pause_music()
        self._playing = False
        
        print(f"ChartPlayer: Pausado en {self.current_time}ms")
    
    def resume(self) -> None:
        """Reanuda la reproducción."""
        if self._playing:
            return
        
        self.audio.unpause_music()
        self._start_tick = pygame.time.get_ticks() - int(self.current_time)
        self._playing = True
        
        print(f"ChartPlayer: Reanudado desde {self.current_time}ms")
    
    def stop(self) -> None:
        """Detiene completamente la reproducción."""
        self.audio.stop_music()
        self._playing = False
        self.current_time = 0.0

        self._active_notes.clear()
        
        print("ChartPlayer: Detenido.")
    
    def toggle_play_pause(self) -> None:
        """Alterna entre play y pause."""
        if self._playing:
            self.pause()
        elif self.current_time == 0:
            self.play()
        else:
            self.resume()
    


    # --- ACTUALIZACIÓN ---
    def update(self, dt: float) -> None:
        """Actualiza el tiempo del chart (llamar cada frame)."""
        if not self._playing:
            return
        
        # Se sincroniza el tiempo real
        self.current_time = float(pygame.time.get_ticks() - self._start_tick)
        
        # Verifica si se llegó al final
        if self.current_time >= self.chart.total_duration:
            self.stop()
            print("ChartPlayer: Chart completado")
    


    # --- OBTENER NOTAS ACTIVAS ---
    def get_active_notes(self) -> list[Note]:
        """
        Obtiene las notas que deben ser visibles en el tiempo actual.
        Usa cache para evitar recalcular en cada frame.
        """
        # Si el tiempo no cambió significativamente, usar cache
        if abs(self.current_time - self._last_cache_time) < 16:  # 1 frame a 60fps
            return self._active_notes
        
        # Recalcular notas activas
        self._active_notes = self.chart.get_all_active_notes(self.current_time, self.spawn_time_ms)
        self._last_cache_time = self.current_time
        
        return self._active_notes
    


    # --- HELPERS ---
    def get_progress_percentage(self) -> float:
        """Calcula el progreso del chart en porcentaje (0-100)."""
        if self.chart.total_duration == 0:
            return 100.0
        return (self.current_time / self.chart.total_duration) * 100
    
    def get_current_section(self):
        """Obtiene la sección activa actual."""
        return self.chart.get_section_at_time(self.current_time)