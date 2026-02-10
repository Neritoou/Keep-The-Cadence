from ...constants import NOTE_SIZE, NOTE_PADDING, PARTICLE_SPLASH_SIZE, PARTICLE_SPLASH_PADDING
from typing import TYPE_CHECKING
from ...util import get_asset

if TYPE_CHECKING:
        from ..resource_manager import ResourceManager
        
def _load_spritesheets(rm: "ResourceManager") -> None:
        # TIPOS DE NOTAS
        rm.load_spritesheet("NotesType", str(get_asset("spritesheets", "notes.png")), NOTE_SIZE, NOTE_PADDING)

        # TIPOS DE PARTICULAS
        rm.load_spritesheet("ParticlesType", str(get_asset("spritesheets", "particles_splash.png")), PARTICLE_SPLASH_SIZE, PARTICLE_SPLASH_PADDING)
