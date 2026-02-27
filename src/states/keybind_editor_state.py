import pygame
from typing import TYPE_CHECKING
from .game_state import GameState
from .types import OverlayType
from ..config.keybind_editor import KeybindEditor
from ..util.conversors import pygame_key_to_str

if TYPE_CHECKING:
    from ..core.game import Game


class KeybindEditorState(GameState):
    """State temporal para probar el KeybindEditor."""
    def __init__(self, game: "Game"):
        super().__init__(game)
        self._editor  = KeybindEditor(game.controls_config)
        self._font    = pygame.font.SysFont("monospace", 24)
        self._font_sm = pygame.font.SysFont("monospace", 18)
        self._max     = game.controls_config.max_keys_for_action

        # Solo acciones navegables
        self._actions: list[tuple[str, str]] = [
            (ctx, act)
            for ctx in self._editor.get_contexts()
            for act in self._editor.get_actions(ctx)
        ]

        self._action_cursor = 0
        self._slot_cursor   = 0

    def _current(self) -> tuple[str, str, int]:
        ctx, act = self._actions[self._action_cursor]
        return ctx, act, self._slot_cursor

    def update(self, dt: float) -> None:
        pass

    def on_enter(self) -> None:
        pass
    
    def on_exit(self) -> None:
        pass
    

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if self._editor.is_capturing:
                if event.key == pygame.K_ESCAPE:
                    self._editor.cancel_capture()
                else:
                    self._editor.assign(event.key)
                return

            match event.key:
                case pygame.K_UP:
                    self._action_cursor = (self._action_cursor - 1) % len(self._actions)
                    self._slot_cursor   = 0
                case pygame.K_DOWN:
                    self._action_cursor = (self._action_cursor + 1) % len(self._actions)
                    self._slot_cursor   = 0
                case pygame.K_LEFT:
                    self._slot_cursor = (self._slot_cursor - 1) % self._max
                case pygame.K_RIGHT:
                    self._slot_cursor = (self._slot_cursor + 1) % self._max
                case pygame.K_RETURN:
                    ctx, act, slot = self._current()
                    self._editor.start_capture(ctx, act, slot)
                case pygame.K_DELETE:
                    ctx, act, slot = self._current()
                    self._editor.clear_slot(ctx, act, slot)
                case pygame.K_s:
                    self._editor.apply()
                    self.game.input.update_controls(self.game.controls_config.data)
                case pygame.K_ESCAPE:
                    self._editor.discard()
                    self.game.state.exit_current()
                    
    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 20, 20))
        y = 40

        status = "[ PRESIONA UNA TECLA... ]" if self._editor.is_capturing else "[ KEYBIND SETTINGS ]"
        color  = (255, 80, 80) if self._editor.is_capturing else (255, 215, 0)
        surface.blit(self._font.render(status, True, color), (40, y))
        y += 50

        current_ctx = None
        for i, (ctx, act) in enumerate(self._actions):
            # --- Header de contexto si cambió ---
            if ctx != current_ctx:
                current_ctx = ctx
                surface.blit(
                    self._font.render(ctx.upper(), True, (180, 140, 255)),
                    (40, y)
                )
                y += 34

            # --- Acción con sus slots ---
            is_active = i == self._action_cursor
            slots     = self._editor.get_slots(ctx, act)

            parts = []
            for s, k in enumerate(slots):
                try:
                    label = pygame_key_to_str(k) if k is not None else "---"
                except ValueError:
                    label = "???"

                if is_active and s == self._slot_cursor:
                    label = f"[{label}]"
                else:
                    label = f" {label} "
                parts.append(label)

            line  = f"  {act:<22}" + "  |  ".join(parts)
            color = (255, 255, 0) if is_active else (200, 200, 200)
            surface.blit(self._font_sm.render(line, True, color), (40, y))
            y += 28

        # --- Estado y ayuda ---
        y += 20
        changed_color = (80, 255, 80) if self._editor.has_changes() else (100, 100, 100)
        surface.blit(
            self._font_sm.render(f"Cambios pendientes: {self._editor.has_changes()}", True, changed_color),
            (40, y)
        )
        y += 28

        for hint in ["↑↓ → acción", "←→ → slot", "ENTER → reasignar", "DEL → borrar", "S → guardar", "ESC → salir"]:
            surface.blit(self._font_sm.render(hint, True, (120, 120, 120)), (40, y))
            y += 24

    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.FULLSCREEN

    @property
    def is_transient(self) -> bool:
        return False