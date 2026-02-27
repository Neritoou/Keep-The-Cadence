from typing import TYPE_CHECKING
from ...util import get_asset

if TYPE_CHECKING:
    from ..resource_manager import ResourceManager

def _load_images(rm: "ResourceManager") -> None:
    
    rm.load_image("Title", str(get_asset("images", "game_title.png")))
    rm.load_image("Background", str(get_asset("images", "filled_background.png")))
    rm.load_image("SplashArt", str(get_asset("images", "miku_splashart.png")))
    rm.load_image("stage_panel", str(get_asset("images","stage","panel.png")))