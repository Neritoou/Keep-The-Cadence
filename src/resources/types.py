from typing import TypedDict
from pygame import Surface
from enum import Enum
from pygame.font import Font
from pygame.mixer import Sound
from .spritesheet import SpriteSheet

class ImageResource(TypedDict):
    path: str
    surface: Surface 

class FontResource(TypedDict):
    path: str
    font: dict[int, Font]

class SpriteSheetResource(TypedDict):
    path: str
    spritesheet: SpriteSheet

class SoundResource(TypedDict):
    path: str
    sound: Sound

class MusicResource(TypedDict):
    path: str

class AudioCategory(Enum):
    """Categorías de audio para control de volumen independiente"""
    MUSIC = "music"
    SFX = "sfx"
    VOICE = "voice"
