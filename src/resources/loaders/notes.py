from typing import TYPE_CHECKING
from ...core.types import NoteDirection
from ...constants import NOTE_SIZE_MULTIPLIER

if TYPE_CHECKING:
    from ..note_library import NoteSurfaces
    from ..resource_manager import ResourceManager
    
def _load_notes(rm: "ResourceManager") -> None:
    """Registra las notas del juego."""
    notes_sheet = rm.get_spritesheet("NotesType") 
    for direction in NoteDirection:
        
        frames = notes_sheet.get_frames_at_col(direction,True,NOTE_SIZE_MULTIPLIER)

        surfaces: NoteSurfaces = {
            "missed": frames[0],
            "default": frames[1],
            "spawned": frames[2],
            "pressed": [frames[3], frames[4], frames[5]],
            "hold": frames[6],
            "end_hold": frames[7]
        }

        particles_sheet = rm.get_spritesheet("ParticlesType")
        particles = particles_sheet.get_frames_at_col(direction,True)

        rm.load_note(direction, surfaces, particles)