import pygame
from typing import TYPE_CHECKING
from ..types import ChartData
from ..note import Note
from ...audio import AudioCategory
from ...util.paths import get_inst_path, get_voices_path

if TYPE_CHECKING:
    from ...audio import AudioManager
    from ..types import Section
    from ..difficulty_data import DifficultyData


class ChartPlayer:
    """
    Controla la reproducción de un chart con sincronización de audio.

    Gestiona el tiempo de la canción usando `pygame.time.get_ticks()` como
    referencia, garantizando que el chart esté siempre sincronizado con el
    audio independientemente de los saltos de frame.

    Attributes:
        chart: Datos del chart cargado.
        audio: Gestor de audio del juego.
        spawn_time_ms: Anticipación en ms con la que las notas aparecen en pantalla.
        current_time: Tiempo actual del chart en milisegundos.
    """
    
    def __init__(self, chart: ChartData, audio_manager: "AudioManager",
                 song_folder: str, spawn_time_ms: float, diff_data: "DifficultyData"):
        """
        Args:
            chart: Chart ya parseado y listo para reproducir.
            audio_manager: Gestor de audio del juego.
            song_folder: Nombre de la carpeta de la canción, usado para
                         resolver los paths de inst y voices.
            spawn_time_ms: Tiempo en ms de anticipación para el spawn de notas.
        """
        self.chart = chart
        self.audio = audio_manager
        self.spawn_time_ms = spawn_time_ms
        self.diff_data = diff_data

        # Paths resueltos de los archivos de audio
        self._inst_path = str(get_inst_path(song_folder))
        self._voices_path = str(get_voices_path(song_folder))

        # Voices se carga completo en RAM como Sound para poder pausarlo
        # por canal, a diferencia del inst que usa pygame.mixer.music
        self._voice_sound = pygame.mixer.Sound(self._voices_path)
        self._voice_channel: pygame.mixer.Channel | None = None
        self._voice_volume = 1.0
        self._is_voice_muted = False
        self.audio.register_sound("song_voices", self._voice_sound, AudioCategory.VOICE)

        # Estado interno de reproducción
        self._playing = False
        self.current_time = 0.0
        self._start_tick = 0 # tick de pygame en el momento en que se inició la reproducción

        # Lista de notas que deben procesarse en el frame actual
        self._active_notes: list[Note] = []

    # --- PROPIEDADES ---
    @property
    def is_playing(self) -> bool:
        """True si el chart se está reproduciendo activamente."""
        return self._playing

    @property
    def is_finished(self) -> bool:
        """True si el tiempo actual superó la duración total de la canción."""
        return self.current_time >= self.chart.song_duration
    
    @property
    def current_section(self) -> "Section":
        """Sección del chart que corresponde al tiempo actual."""
        return self.chart.current_section


    # --- CONTROL DE REPRODUCCIÓN ---
    def play(self, start_time: float = 0.0) -> None:
        """
        Inicia la reproducción sincronizada de inst y voices.

        El inst se reproduce mediante `pygame.mixer.music` y las voices
        mediante un canal de Sound para poder pausarlas independientemente.

        Args:
            start_time: Tiempo en ms desde donde iniciar la reproducción.
        """
        self.audio.play_music(self._inst_path, loops=0, start=start_time / 1000)
        self._voice_channel = self._voice_sound.play()

        if self._is_voice_muted and self._voice_channel:
            self._voice_channel.set_volume(0.0)

        self.current_time = start_time
        self._start_tick = pygame.time.get_ticks() - int(start_time)
        self._playing = True

    def pause(self) -> None:
        """Pausa inst y voices de forma sincronizada."""
        if not self._playing:
            return

        self.audio.pause_music()
        if self._voice_channel:
            self._voice_channel.pause()

        self._playing = False

    def resume(self) -> None:
        """Reanuda inst y voices de forma sincronizada."""
        if self._playing:
            return

        self.audio.unpause_music()
        if self._voice_channel:
            self._voice_channel.unpause()

        self._start_tick = pygame.time.get_ticks() - int(self.current_time)
        self._playing = True

    def stop(self) -> None:
        """Detiene completamente la reproducción y audio del estado interno."""
        self.audio.stop_music()

        if self._voice_channel:
            self._voice_channel.stop()
            self._voice_channel = None

        self.audio.stop_all_sounds()
        self._playing = False

    def reset(self) -> None:
        """Resetea el chart al estado inicial para poder volver a reproducirlo."""
        if self._is_voice_muted:
            self.unmute_voices()

        self.chart.reset()
        self.current_time = 0.0
        self._active_notes.clear()
        

    def cleanup(self) -> None:
        """
        Libera el sonido de voices del AudioManager.
        
        Debe llamarse desde PlayState.on_exit() siempre DESPUÉS de stop(),
        ya que stop() detiene el canal antes de que el Sound sea liberado.
        """
        self.audio.unregister_sound("song_voices", AudioCategory.VOICE)

    def toggle_play_pause(self) -> None:
        """Alterna entre play y pausa según el estado actual."""
        if self._playing:
            self.pause()
        elif self.current_time == 0.0:
            self.play()
        else:
            self.resume()


    # --- CONTROL DE VOCES ---
    def mute_voices(self) -> None:
        """
        Silencia las voices guardando el volumen previo para restaurarlo después.
        Se llama cuando el personaje entra en estado de fallo.
        """
        if self._is_voice_muted:
            return
        self._voice_volume = self.audio.get_category_volume(AudioCategory.VOICE)
        self._is_voice_muted = True
        self.audio.set_category_volume(AudioCategory.VOICE, 0.0)

    def unmute_voices(self) -> None:
        """
        Restaura el volumen de voices al valor previo al mute.
        Se llama cuando el personaje vuelve a un estado de acierto.
        """        
        if not self._is_voice_muted:
            return
        self.audio.set_category_volume(AudioCategory.VOICE, self._voice_volume)
        self._is_voice_muted = False
    
    # --- MISSES AUTOMÁTICOS ---
    def pop_missed_notes(self) -> list[Note]:
        """
        Detecta y marca como MISSED las notas cuya ventana de hit expiró.

        Debe llamarse siempre DESPUÉS de update() en el mismo frame para
        garantizar que _active_notes esté actualizado al tiempo correcto.

        Returns:
            Lista de notas que acaban de pasar a estado MISSED en este frame.
        """
        missed = []
        for note in self._active_notes:
            if note.is_missed(self.current_time, self.diff_data.judgement_windows):
                note.on_missed()
                missed.append(note)
        return missed
    
    # --- ACTUALIZACIÓN ---
    def update(self, dt: float) -> None:
        """Avanza el tiempo del chart y refresca las notas activas."""
        if not self._playing:
            return

        self.current_time = float(pygame.time.get_ticks() - self._start_tick)
        self.chart.advance_section(self.current_time)
        self._active_notes = self.chart.get_current_notes(self.current_time, self.spawn_time_ms)

        if self.current_time >= self.chart.song_duration:
            self.stop()

    # --- HELPERS ---
    def get_progress_percentage(self) -> float:
        """Calcula el porcentaje de progreso de la canción."""
        if self.chart.song_duration == 0:
            return 100.0
        return (self.current_time / self.chart.song_duration) * 100
    



