from typing import TYPE_CHECKING
from ...util import get_asset
from ..types import AudioCategory

if TYPE_CHECKING:
        from ..resource_manager import ResourceManager

def _load_sounds(rm: "ResourceManager"):
        # MISS SOUNDS
        for i in range(1, 4):
            rm.load_sound(f"miss_note_{i}", AudioCategory.SFX, str(get_asset("sounds", "miku", f"miss_note_{i}.ogg")))

        # COUNTDOWN SOUNDS
        for i in range(0, 4):
            rm.load_sound(f"countdown_{i}", AudioCategory.SFX, str(get_asset("sounds", "countdown", f"countdown_{i}.ogg")))

        # MENU SOUNDS
        rm.load_sound("scroll", AudioCategory.SFX, str(get_asset("sounds", "menu", "scroll_menu.ogg")))
        rm.load_sound("select", AudioCategory.SFX, str(get_asset("sounds", "menu", "confirm_menu.ogg")))


