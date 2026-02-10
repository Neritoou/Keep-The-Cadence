from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..note_library import NoteSurfaces
    from ..resource_manager import ResourceManager
    
def _load_notes(rm: "ResourceManager") -> None:
    """Registra las notas del juego."""
    notes_sheet = rm.get_spritesheet("NotesType") 

    for col in range(0, 3):
        
        frames = notes_sheet.get_frames_at_col(col)
        notes: NoteSurfaces = {
            "missed": frames[0],
            "default": frames[1],
            "spawned": frames[2],
            "pressed": [frames[3], frames[4], frames[5]],
            "hold": frames[6],
            "end_hold": frames[7]
        }

        particles_sheet = rm.get_spritesheet("ParticlesType")
        particles = particles_sheet.get_frames_at_col(col)

        rm.load_note(col, notes, particles)