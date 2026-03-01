from typing import TYPE_CHECKING
from ...util import get_asset

if TYPE_CHECKING:
        from ..resource_manager import ResourceManager

def _load_music_paths(rm: "ResourceManager"):
        rm.load_music_path("freaky", str(get_asset("sounds", "menu", "freaky_menu.ogg")))
        rm.load_music_path("win", str(get_asset("sounds", "states", "win.ogg")))