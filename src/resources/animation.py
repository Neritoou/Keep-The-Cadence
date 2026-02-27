import pygame
from ..constants import MAX_DT_PER_UPDATE_ANIMATION

class Animation:
    """
    Maneja animaciones basadas en sprites utilizando superficies de Pygame.
    
    Args:
        animations (dict[str, list[pygame.Surface]]): Diccionario nombre -> frames
        fps_map (dict[str, int]): FPS específico por animación
        current_animation (str): Nombre de la animación activa
        frames (list[pygame.Surface]): Frames de la animación actual
        base_fps (int): FPS por defecto
        loop (bool): Si la animación se reproduce en bucle
        frame_index (int): Índice del frame actual
        playing (bool): Si está reproduciéndose
    """    
    def __init__(
        self,
        animations: dict[str, list[pygame.Surface]],
        default: str,
        base_fps: int = 8,
        loop: bool = True,
        fps_map: dict[str, int] | None = None,
        bpm: float | None = None
    ) -> None:
        """
        Inicializa el sistema de animación.
        
        Args:
            animations (dict[str, list[pygame.Surface]]): Diccionario nombre -> frames
            default: Nombre de la animación inicial
            base_fps: FPS por defecto (mínimo 1)
            loop: Si las animaciones deben hacer loop por defecto
            fps_map: FPS específico para ciertas animaciones
            bpm: BPM inicial para sincronización (None = desactivado)
        """
        self._assert_animations(animations, default)
    
        # Datos de animación
        self.animations = animations
        self.fps_map = fps_map or {}

        # Estado actual
        self.current_animation = default
        self.frames = animations[default]
        self.frame_index = 0
        
        # Configuración
        self.base_fps = max(1, base_fps)
        self.loop = loop
        
        # Control de reproducción
        self.playing = True
        self.time_acc = 0.0
        self._frame_time = self._calculate_frame_time()

        # Beat Sync
        self._ms_per_beat: float | None = (60000.0 / bpm) if bpm is not None else None
        self._beat_timer: float = 0.0

    def play(self, name: str, reset: bool = False, loop: bool | None = None, start_frame: int = 0) -> None:
        """
        Cambia y reproduce una animación.
        
        Args:
            name: Nombre de la animación a reproducir
            reset: Si True, reinicia aunque ya esté activa
            loop: Sobrescribe el loop default (None = usar default)
            start_frame: Frame inicial (default 0)
        """
        # Si es la misma animación y no se pide reset
        if name == self.current_animation and not reset:
            return
        
        if name not in self.animations:
            raise ValueError(f"Animation: '{name}' does not exist")
        
        # Cambiar animación
        self.current_animation = name
        self.frames = self.animations[name]
        
        # Validar start_frame
        if start_frame < 0 or start_frame >= len(self.frames):
            raise IndexError(
                f"Animation: start_frame {start_frame} fuera de Rango"
                f"[0-{len(self.frames)-1}]"
            )
        
        # Resetear estado
        self.frame_index = start_frame
        self.time_acc = 0.0
        self.playing = True
        
        # Actualizar loop si se especificó
        if loop is not None:
            self.loop = loop
        
        # Recalcular frame_time
        self._frame_time = self._calculate_frame_time()
    
    def pause(self) -> None:
        """Pausa la animación."""
        self.playing = False
    
    def resume(self) -> None:
        """Reanuda la animación."""
        self.playing = True
    
    def reset(self) -> None:
        """Resetea la animación actual al frame 0."""
        self.frame_index = 0
        self.time_acc = 0.0
        self.playing = True
    
    def stop(self) -> None:
        """Detiene y resetea la animación."""
        self.playing = False
        self.frame_index = 0
        self.time_acc = 0.0
    
    def update(self, dt: float) -> None:
        """Actualiza la animación según el tiempo transcurrido."""
        if not self.playing or len(self.frames) <= 1:
            return
                
        # Beat sync — reinicia la animación en cada beat si está activado
        if self._ms_per_beat is not None:
            self._beat_timer += dt * 1000
            if self._beat_timer >= self._ms_per_beat:
                self._beat_timer -= self._ms_per_beat
                self.frame_index = 0
                self.time_acc    = 0.0

        # Protección contra lag
        dt = min(dt, MAX_DT_PER_UPDATE_ANIMATION)
        
        self.time_acc += dt
        
        # Avanzar frames
        while self.time_acc >= self._frame_time:
            self.time_acc -= self._frame_time
            self.frame_index += 1
            
            # Verificar si llegó al final
            if self.frame_index >= len(self.frames):
                if self.loop:
                    self.frame_index = 0
                    
                else:
                    # Quedarse en último frame
                    self.frame_index = len(self.frames) - 1
                    self.playing = False
                    break

    def draw(self, surface: pygame.Surface, position: tuple[int,int]):
        """
        Dibuja el frame actual en una posición determinada.

        Args:
            surface: Superficie de Pygame donde dibujar.
            position: Tupla (x, y) indicando la esquina superior izquierda.
        """
        frame = self.frames[self.frame_index]
        surface.blit(frame, frame.get_rect(topleft=position))

    def draw_centered(self, surface: pygame.Surface, center: tuple[int,int]):
        """
        Dibuja el frame actual centrado en un punto.

        Args:
            surface: Superficie de Pygame donde dibujar.
            center: Tupla (x, y) indicando el centro del frame.
        """
        frame = self.frames[self.frame_index]
        surface.blit(frame, frame.get_rect(center=center))

    #  CONFIGURACIÓN

    def set_loop(self, loop: bool) -> None:
        """Configura si la animación actual se reproduce en bucle."""
        self.loop = loop

    def set_base_fps(self, fps: int) -> None:
        """Establece el FPS base para animaciones sin FPS específico."""
        self.base_fps = max(1, fps)
        self._frame_time = self._calculate_frame_time()

    def set_fps_for_animation(self, animation_name: str, fps: int) -> None:
        """Establece FPS específico para una animación."""
        self.fps_map[animation_name] = max(1, fps)
        if self.current_animation == animation_name:
            self._frame_time = self._calculate_frame_time()

    def go_to_frame(self, frame_index: int) -> None:
        """Salta a un frame específico."""
        if frame_index < 0 or frame_index >= len(self.frames):
            raise IndexError(
                f"Animation: frame_index {frame_index} out of range "
                f"[0-{len(self.frames) - 1}]"
            )
        self.frame_index = frame_index
        self.time_acc = 0.0

    def sync_to_bpm(self, bpm: float) -> None:
        """
        Sincroniza la animación al BPM — se reinicia en cada beat.

        Args:
            bpm: Beats por minuto de la canción.
        """
        self._ms_per_beat = 60000.0 / bpm
        self._beat_timer = 0.0

    def unsync(self) -> None:
        """Desactiva la sincronización al BPM."""
        self._ms_per_beat = None
        self._beat_timer = 0.0

    # --- CONSULTAS ---

    def is_playing(self) -> bool:
        """Verifica si la animación está reproduciéndose."""
        return self.playing

    def is_last_frame(self) -> bool:
        """Verifica si llegó al último frame."""
        return self.frame_index >= len(self.frames) - 1

    def get_current_frame(self) -> pygame.Surface:
        """Obtiene el frame actual."""
        return self.frames[self.frame_index]

    def get_current_frame_index(self) -> int:
        """Obtiene el índice del frame actual."""
        return self.frame_index

    def get_frame_count(self) -> int:
        """Obtiene el número total de frames de la animación actual."""
        return len(self.frames)

    def get_animation_duration(self) -> float:
        """Calcula la duración total de la animación en segundos."""
        return len(self.frames) * self._frame_time

    def get_current_animation_name(self) -> str:
        """Obtiene el nombre de la animación actual."""
        return self.current_animation

    def has_animation(self, name: str) -> bool:
        """Verifica si existe una animación con ese nombre."""
        return name in self.animations

    def get_animations(self) -> dict[str, list[pygame.Surface]]:
        """Obtiene todas las animaciones disponibles."""
        return self.animations

    #  --- HELPERS ---

    def _assert_animations(self, animations: dict[str, list[pygame.Surface]],
                            default: str) -> None:
        if not animations:
            raise ValueError("Animation: animations dict cannot be empty")
        if default not in animations:
            raise ValueError(f"Animation: default '{default}' does not exist")
        for name, frames in animations.items():
            if not frames:
                raise ValueError(f"Animation: '{name}' has no frames")

    def _calculate_frame_time(self) -> float:
        """Calcula la duración de un frame en segundos."""
        fps = self.fps_map.get(self.current_animation, self.base_fps)
        return 1.0 / max(1, fps)