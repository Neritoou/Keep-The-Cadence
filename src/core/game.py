import pygame
from enfocate import GameBase, GameMetadata, COLORS
from ..resources import ResourceManager
from ..controller import InputManager
from ..audio import AudioManager
from ..states import *
from ..config import *

class Game(GameBase):
    def __init__(self, metadata: GameMetadata) -> None:
        # 1. Inyección de metadatos al Core
        super().__init__(metadata)

        # 2. Inicialización de estado interno
        self.controls_config = ControlsConfig(path="config/controls.json")
        self.resources: ResourceManager = ResourceManager()
        self.input = InputManager(self.controls_config.data)
        self.state: StateManager = StateManager(self)
        self.audio: AudioManager = AudioManager()

    def on_start(self) -> None:
        # Cargar Recursos
        self.resources.load()
        self.audio.register_sounds(self.resources.get_sounds())

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