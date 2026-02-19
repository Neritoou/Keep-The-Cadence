from pygame import Surface
from ..resources import Animation
from .types import NoteDirection
from .receptor_state import ReceptorState, ReceptorFSM
from ..constants import MAX_SING_DURATION

class Character:
    """
    Personaje jugable que reacciona visualmente a las notas.

    Gestiona sus animaciones mediante una FSM (ReceptorFSM) con los mismos
    estados que el receptor: IDLE, HOLD_HIT, HOLD_MISS, RELEASE_HIT, RELEASE_MISS.

    Animaciones requeridas:
        - idle
        - sing_left, sing_down, sing_up, sing_right
        - miss_left, miss_down, miss_up, miss_right

    Args:
        animations: Diccionario de nombre → lista de frames.
        position: Posición (x, y) donde se dibuja centrado.
        bpm: BPM de la canción, afecta la velocidad de animación.
    """
    def __init__(self, animations: dict[str, list[Surface]], position: tuple[int, int], bpm: float = 120.0):
        self._validate_animations(animations)

        self.position = position
        self.bpm = bpm
        self.receptor = ReceptorFSM()

        self.animator = Animation(
            animations = animations,
            default = "idle",
            base_fps = 10,
            loop=True
        )

        # Duración mínima de la animación de canto antes de volver a idle.
        self._sing_duration = 0.0
        self._recalculate_timing()

    # (!) CAMBIAR POSTERIORMENTE A SINCRONIZACIÓN CON BEAT DE LA CANCIÓN
    def _recalculate_timing(self) -> None:
        """Recalcula duraciones dependientes del BPM."""
        self._sing_duration = MAX_SING_DURATION

    def update_bpm(self, value: float) -> None:
        """Actualiza BPM del personaje (no cambia FPS)."""
        self.bpm = value
        self._recalculate_timing()

    # --- INPUT ---
    def press_hit(self, direction: NoteDirection) -> None:
        """Notifica al personaje que se acertó una nota."""
        self.receptor.state = ReceptorState.HOLD_HIT
        self.receptor.direction = direction
        self.receptor.timer = 0.0

    def press_miss(self, direction: NoteDirection) -> None:
        """Notifica al personaje que se falló una nota."""
        self.receptor.state = ReceptorState.HOLD_MISS
        self.receptor.direction = direction
        self.receptor.timer = 0.0

    def release_key(self, direction: "NoteDirection") -> None:
        """Notifica al personaje que se soltó una tecla."""
        if self.receptor.direction != direction:
            return
        
        match self.receptor.state:
            case ReceptorState.HOLD_HIT:
                self.receptor.state = ReceptorState.RELEASE_HIT
            case ReceptorState.HOLD_MISS:
                self.receptor.state = ReceptorState.RELEASE_MISS

    # --- UPDATE ---
    def update(self, dt: float) -> None:
        """Actualiza la FSM y la animación del personaje."""
        match self.receptor.state:
            case ReceptorState.IDLE:
                self._update_idle(dt)
            case ReceptorState.HOLD_HIT:
                self._update_hold_hit(dt)
            case ReceptorState.HOLD_MISS:
                self._update_hold_miss(dt)
            case ReceptorState.RELEASE_HIT:
                self._update_release_hit(dt)
            case ReceptorState.RELEASE_MISS:
                self._update_release_miss(dt)

    def _update_idle(self,dt:float) -> None:
        if self.animator.get_current_animation_name() != "idle":
            self.animator.play("idle", reset=True, loop=True)

        self.animator.update(dt)

    def _update_hold_hit(self, dt: float) -> None:
        anim_name = self._get_animation_name()
        self.receptor.timer += dt

        if self.animator.get_current_animation_name() != anim_name:
            self.animator.play(anim_name, reset=True, loop=True)

        self.animator.update(dt)

    def _update_hold_miss(self, dt: float) -> None:
        anim_name = self._get_animation_name()
        self.receptor.timer += dt

        if self.animator.get_current_animation_name() != anim_name:
            self.animator.play(anim_name, reset=True, loop=False)

        self.animator.update(dt)

    def _update_release_hit(self, dt: float) -> None:
        anim_name = self._get_animation_name()
        self.receptor.timer += dt

        if self.animator.get_current_animation_name() != anim_name:
            self.animator.play(anim_name, reset=False, loop=False)

        self.animator.update(dt)

        if self.receptor.timer >= self._sing_duration:
            self._go_idle()

    def _update_release_miss(self, dt: float) -> None:
        anim_name = self._get_animation_name()

        self.receptor.timer += dt

        if self.animator.get_current_animation_name() != anim_name:
            self.animator.play(anim_name, reset=False, loop=False)

        self.animator.update(dt)

        if self.receptor.timer >= self._sing_duration:
            self._go_idle()

    def _go_idle(self) -> None:
        self.receptor.state = ReceptorState.IDLE
        self.receptor.direction = None
        self.receptor.timer = 0.0
        self.animator.play("idle", reset=True, loop=True)

    # --- DIBUJAR PERSONAJE ---
    def draw(self, surface: Surface) -> None:
        self.animator.draw_centered(surface, self.position)

    # --- HELPERS ---
    def _validate_animations(self, animations: dict) -> None:
        required = {"idle"}
        for direction in NoteDirection:
            name = direction.name.lower()
            required.add(f"sing_{name}")
            required.add(f"miss_{name}")

        missing = required - set(animations.keys())
        if missing:
            raise ValueError(f"Character: Faltan animaciones: {missing}")
        
    def _get_animation_name(self) -> str:
        """Devuelve el nombre de la animación según el estado y dirección actuales."""
        if self.receptor.direction is None:
            return "idle"

        name = self.receptor.direction.name.lower()

        if self.receptor.state in (ReceptorState.HOLD_HIT, ReceptorState.RELEASE_HIT):
            return f"sing_{name}"

        return f"miss_{name}"