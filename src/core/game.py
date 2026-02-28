import pygame
from enfocate import GameBase, GameMetadata, COLORS
from ..resources import ResourceManager
from ..controller import InputManager
from ..audio import AudioManager
from ..states import *
from ..config import *
from ..core.character_factory import CharacterFactory
from ..core.types import NoteDirection, ScrollDirection
from ..core.note_renderer import NoteRenderer
from ..constants import HIT_LINE_XS, HIT_LINE_Y_UP, SPAWN_TIME_MS, MISS_DISPLAY, MIKU_PLAY_POSITION
from ..core.database import Database
from ..util import get_path
from ..resources import Animation

class Game(GameBase):
    def __init__(self, metadata: GameMetadata) -> None:
        # 1. Inyección de metadatos al Core
        super().__init__(metadata)

        # 2. Inicialización de estado interno
        self.controls_config = ControlsConfig(path="config/controls.json")
        self.resources = ResourceManager()
        self.database = Database(get_path("src","core","database","game_data.json"))
        self.input = InputManager(self.controls_config.data)

        self.state = StateManager(self)
        self.audio = AudioManager()

    def on_start(self) -> None:
        # Cargar Recursos
        self.resources.load()
        self.audio.register_sounds(self.resources.get_sounds())
        self.database.load()

        self.character = CharacterFactory.create_miku(self.resources,MIKU_PLAY_POSITION)

        self.note_renderer = NoteRenderer(
            self.resources.get_all_notes(), HIT_LINE_XS, HIT_LINE_Y_UP,
            ScrollDirection.UP, SPAWN_TIME_MS, MISS_DISPLAY, 720
        )

        sheet = self.resources.get_spritesheet("StageNormies")
        
        normies = sheet.get_frames_at_col(0)
        self.bg_normies = Animation({"bg": normies},"bg", 10)

        self._PLAY_ACTIONS: list[tuple[str, NoteDirection]] = [
            ("left",  NoteDirection.LEFT),
            ("down",  NoteDirection.DOWN),
            ("up",    NoteDirection.UP),
            ("right", NoteDirection.RIGHT),
        ]

        # Estado inicial  
        self.state.change(StateID.MENU)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        self.input.update(events)
        self.state.handle_input(events)

    def update(self, dt: float) -> None:
        self.state.update(dt)

    def draw(self) -> None:
        self.surface.fill(COLORS["violeta_pastel"])
        self.state.render(self.surface)