import pygame
from ..resources import ResourceManager
from ..constants import BASE_RESOLUTION, DEFAULT_FPS
from ..controller import InputManager
from ..states import *
from ..config import *

class Game:
    def __init__(self, title: str) -> None:
        self.title = title
        self._running = False
        self.__surface = None
        self.controls_config = ControlsConfig(path="config/controls.json")
        self.resources: ResourceManager = ResourceManager()
        self.input = InputManager(self.controls_config.data)
        self.state: StateManager = StateManager(self)

    def start(self, surface: pygame.Surface) -> None:
        """
        Marca el juego como activo.
        - Se llama cada vez que el usuario inicia el juego desde el menú del Core.
        - A este método se le debe pasar una superficie en la que el juego se dibujará.

        args:
            **screen**: Pantalla o superficie en la que el juego se dibujará.
        """
        self._running = True
        self.__surface = surface
        # Cargar Recursos 
        self.resources.load()
        # Estado inicial       
        self.state.change(StateID.MENU)

    def stop(self) -> None:
        """
        Detiene el juego, libera recursos dinámicos si es necesario.
        - Se llama cuando el usuario vuelve al menú o cierra el juego.
        """
        self._running = False

    @property
    def running(self) -> bool:
        """
        Devuelve el estado actual del juego (activo o no).
        Útil para el Core para saber si debe llamar a update() y render().
        """
        return self._running
    
    @property
    def surface(self) -> pygame.Surface:
        """
        Devuelve la superficie actual en la que el juego se está dibujando.
        """
        if not self.__surface:
            raise AttributeError("No hay ninguna superficie disponible")
        return self.__surface

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Recibe los eventos que pasan por el Core (teclado, mouse, joystick)
        y los procesa para la lógica del juego.
        - Nunca debe llamar a `pygame.event.get()` por sí mismo.

        args:
            **events**: lista de eventos de pygame capturados en el frame actual
        """
        self.input.update(events)
        self.state.handle_input(events)

    def update(self, dt: float) -> None:
        """
        Actualización de la lógica del juego por frame.
        - Se llama solo si `_running=True`.

        args:
            **dt**: tiempo en segundos desde el último frame (para movimientos independientes del FPS)
        """
        self.state.update(dt)

    def render(self) -> None:
        """
        Dibuja todo el estado del juego en la superficie que pasa el Core.
        - Nunca crea su propia ventana.
        - Se llama solo si `_running=True`.
        """
        self.surface.fill((0, 0, 0))
        self.state.render(self.surface)

    def run(self) -> None:
        """
        Ejecuta el juego de forma independiente sin necesidad del Core.
        Útil para desarrollo y testing.
        """
        screen = pygame.display.set_mode(BASE_RESOLUTION)
        pygame.display.set_caption(self.title)
        clock = pygame.time.Clock()
        self.start(screen)

        try:
            while self._running:
                events = pygame.event.get()

                for event in events:
                    if event.type == pygame.QUIT:
                        self.stop()
                        break

                if self._running:
                    self.handle_events(events)

                if self._running:
                    dt = clock.get_time() / 1000.0
                    self.update(dt)

                if self._running:
                    self.render()
                    pygame.display.flip()

                clock.tick(DEFAULT_FPS)

        except KeyboardInterrupt:
            pass
        
        finally:
            self.stop()
            pygame.quit()