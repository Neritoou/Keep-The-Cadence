import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.types import NoteData, NoteDataType, NoteSurfaces

class NoteLibrary:
    """Clase que gestiona la superficie de las notas y sus partículas."""
    def __init__(self) -> None:
        """Inicializa el registro de notes_notes vacío."""
        self._notes: "NoteDataType" = {}



    # --- MÉTODOS ACCESIBLES ---
    def register_note(
            self, direction: int, notes: "NoteSurfaces", particles: list[pygame.Surface]
            ) -> None:
        """Registra una nueva nota en la biblioteca."""
        self._assert_valid_register(direction)

        self._notes[direction] = {
            "notes": notes,
            "particles": particles
        }
    
    def get_note(self, direction: int) -> "NoteData":
        """Devuelve los datos completos de la nota."""
        self._assert_valid_note(direction)
        return self._notes[direction]
    
    def get_note_surface(self, direction: int, state: str = "spawned") -> pygame.Surface:
        """Obtiene la superficie de la nota para el tipo dado ('default', 'spawned', 'pressed'...)."""
        self._assert_valid_note(direction)
        return self._notes[direction]["notes"][state]
    
    def get_particle_surface(self, direction: int, index: int = 1) -> pygame.Surface:
        """Obtiene la superficie de una partícula."""
        self._assert_valid_note(direction)
        return self._notes[direction]["particles"][index]
    
    @property
    def notes(self) -> "NoteDataType":
        """Devuelve el diccionario completo de notes."""
        return self._notes
    


    # --- HELPERS PRIVADOS ---
    def _assert_valid_register(self, direction: int) -> None:
        """Lanza un ValueError si se intenta registrar una nota ya cargada."""
        if direction in self._notes:
            raise ValueError(f"NoteLibrary: La nota con dirección '{direction}' ya se encuentra registrada.")
    
    def _assert_valid_note(self, direction: int) -> None:
        """Lanza un ValueError si se intenta acceder a una nota no registrada."""
        if direction not in self._notes:
            raise ValueError(
                f"NoteLibrary: La nota con dirección '{direction}' no se ha registrado. "
                f"Notas disponibles: {list(self._notes.keys())}"
            )