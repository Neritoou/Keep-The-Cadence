import pygame

class MusicEditorController:
    """
    Controlador de música para el editor.
    Wrapper simple del AudioManager para uso específico del editor.
    """
    
    def __init__(self, music_path: str, base_pixels_per_ms: float) -> None:
        self.music_path = music_path
        
        # Cargar música
        pygame.mixer.music.load(music_path)
        
        # Estado
        self.playing = False
        self.loop_enabled = True
        self.start_time = 0
        self.current_time = 0

        # Velocidad en pixeles
        self._base_pixels_per_ms = base_pixels_per_ms
        self._pixels_per_ms = base_pixels_per_ms

    # --- PROPERTIES ---
    @property
    def pixels_per_ms(self) -> float:
        """Píxeles por milisegundo"""
        return self._pixels_per_ms
    
    @pixels_per_ms.setter
    def pixels_per_ms(self, value: float) -> None:
        """Ajusta píxeles por milisegundo (con validación)"""
        self._pixels_per_ms = round(max(self._base_pixels_per_ms, value), 3)

    # --- SONG CONTROL ---
    def play(self, start_position: float = 0.0) -> None:
        """
        Reproduce desde una posición específica.
        
        Args:
            start_position: Posición inicial en ms
        """
        start_seconds = start_position / 1000
        pygame.mixer.music.play(start=start_seconds)
        self.start_time = pygame.time.get_ticks() - int(start_position)
        self.playing = True
    
    def pause(self) -> None:
        """Pausa la música"""
        pygame.mixer.music.pause()
        self.playing = False
    
    def unpause(self) -> None:
        """Reanuda la música"""
        pygame.mixer.music.unpause()
        self.start_time = pygame.time.get_ticks() - self.current_time
        self.playing = True
    
    def stop(self) -> None:
        """Detiene la música"""
        pygame.mixer.music.stop()
        self.playing = False
        self.current_time = 0
    
    def toggle_play_pause(self) -> None:
        """Alterna entre play y pause"""
        if self.playing:
            self.pause()
        elif self.current_time == 0:
            self.play()
        else:
            self.unpause()
    
    def toggle_loop(self) -> None:
        """Alterna modo loop"""
        self.loop_enabled = not self.loop_enabled
    
    def update(self) -> None:
        """Actualiza el tiempo actual (llamar cada frame)"""
        if self.playing:
            self.current_time = pygame.time.get_ticks() - self.start_time

    # --- HELPERS ---
    def has_reached(self, time_ms: float) -> bool:
        """Verifica si se alcanzó un tiempo específico"""
        return self.playing and self.current_time >= time_ms
    
    def get_song_length(self) -> int:
        """Obtiene la duración de una musica en milisegundos"""
        try:
            sound = pygame.mixer.Sound(self.music_path)
            return int(round(sound.get_length() * 1000))
        except Exception as e:
            print(f"MusicController in ChartEditor: Error obteniendo duración: {e}")
            raise RuntimeError("MusicController in ChartEditor: No se pudo obtener la duración de la canción.")
        

