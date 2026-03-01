from typing import TYPE_CHECKING
from ...util import get_asset

if TYPE_CHECKING:
    from ..resource_manager import ResourceManager

def _load_images(rm: "ResourceManager") -> None:
    # Fondos
    rm.load_image("Background", str(get_asset("images", "filled_background.png")))
    rm.load_image("Background2", str(get_asset("images", "select_background.png")))
    rm.load_image("Background3", str(get_asset("images", "credits_background.png")))
    rm.load_image("Background4", str(get_asset("images", "controls_background.png")))

    rm.load_image("Title", str(get_asset("images", "game_title.png")))
    rm.load_image("SplashArt", str(get_asset("images", "miku_splashart.png")))

    rm.load_image("stage_panel", str(get_asset("images","stage","panel.png")))

    rm.load_image("Record", str(get_asset("images", "record_small.png")))

    rm.load_image("MenuArrows", str(get_asset("images", "menu_arrows.png")))