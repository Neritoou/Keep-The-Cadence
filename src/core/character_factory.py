from typing import TYPE_CHECKING
from .character import Character
from .types import NoteDirection
from ..constants import MIKU_SIZE_MULTIPLIER

if TYPE_CHECKING:
    from ..resources import ResourceManager
    from pygame import Surface

class CharacterFactory:
    """Factory para crear personajes desde spritesheets"""
    
    @staticmethod
    def create_miku(resource_manager: "ResourceManager", position: tuple[int, int] = (900, 400) ) -> Character:
        """Retorna instancia de Character configurado con las animaciones de Miku"""        
        animations = CharacterFactory._load_miku_animations(resource_manager)
        return Character(animations, position)
    
    @staticmethod
    def _load_miku_animations(rm: "ResourceManager") -> "dict[str, list[Surface]]":
        """Carga las animaciones de Miku desde spritesheets"""
        animations = {}
        
        # IDLE
        animations["idle"] = rm.get_spritesheet("MIKU_IDLE").get_frames_at_row(0,True,MIKU_SIZE_MULTIPLIER)
        # HEY
        animations["hey"] = rm.get_spritesheet("MIKU_HEY").get_frames_at_row(0,True,MIKU_SIZE_MULTIPLIER)
        # WIN
        sheet = rm.get_spritesheet("MIKU_WIN")
        animations["win"] = [frame for i in range(5) for frame in sheet.get_frames_at_row(i,True,MIKU_SIZE_MULTIPLIER)]

        # SING DIRECTIONS
        directions_sheet = rm.get_spritesheet("MIKU_DIRECTIONS")
        miss_sheet = rm.get_spritesheet("MIKU_MISS_DIRECTIONS")

        for direction in NoteDirection:
            name = direction.name.lower()
            col = direction.value
            animations[f"sing_{name}"] = directions_sheet.get_frames_at_col(col,True,MIKU_SIZE_MULTIPLIER)
            animations[f"miss_{name}"] = miss_sheet.get_frames_at_col(col,True,MIKU_SIZE_MULTIPLIER)
        
        return animations