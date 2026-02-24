from typing import TYPE_CHECKING
from ...util import get_asset
from ..types import AudioCategory

if TYPE_CHECKING:
        from ..resource_manager import ResourceManager

def _load_sounds(rm: "ResourceManager"):
        rm.load_sound("miss_note_1",AudioCategory.SFX,str(get_asset("sounds","miku","miss_note_1.ogg")))
        rm.load_sound("miss_note_2",AudioCategory.SFX,str(get_asset("sounds","miku","miss_note_2.ogg")))
        rm.load_sound("miss_note_3",AudioCategory.SFX,str(get_asset("sounds","miku","miss_note_3.ogg")))