from typing import TYPE_CHECKING
from ...util import get_asset

if TYPE_CHECKING:
        from ..resource_manager import ResourceManager

def _load_fonts(rm: "ResourceManager") -> None:
        different_sizes = {48, 90}
        rm.load_font("Estandar", str(get_asset("fonts","04B03.ttf")), different_sizes)
