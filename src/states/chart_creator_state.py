import pygame
from .game_state import GameState
from .types import OverlayType, StateID
from ..core.chart_editor import ChartEditor
from ..core.types import NoteDirection, ScrollDirection
from ..constants import BASE_PIXELS_PER_MS, SPAWN_TIME_MS, HIT_LINE_Y_UP, HIT_LINE_XS_EDITOR
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.game import Game

class ChartCreatorState(GameState):
    """Estado del editor de charts"""
    
    def __init__(self, game: "Game", bpm: int, song_path: str, song_name: str, chart_path: str):
        super().__init__(game)
        notes = self.game.resources.get_all_notes()
        self.editor = ChartEditor(notes_data = notes,
            song_path = song_path,
            song_name = song_name,
            bpm = bpm, 
            chart_path = chart_path,
            hit_line_y = HIT_LINE_Y_UP, 
            hit_line_xs = HIT_LINE_XS_EDITOR, 
            scroll_direction = ScrollDirection.UP,
            spawn_time_ms = SPAWN_TIME_MS,
            base_pixels_per_ms = BASE_PIXELS_PER_MS,
        )

        self.key_to_direction = {
            pygame.K_w: NoteDirection.UP,
            pygame.K_a: NoteDirection.LEFT,
            pygame.K_s: NoteDirection.DOWN,
            pygame.K_d: NoteDirection.RIGHT
        }

    
    def update(self, dt):
        self.editor.update(dt)


    def render(self, surface):
        self.editor.render(surface)
    
    def handle_input(self, events):
        # NOTAS
        for key, direction in self.key_to_direction.items():
            # Presionar            

            if self.game.input.is_key_pressed(key):
                self.editor.on_key_press(direction)

            elif self.game.input.is_key_held(key):
                self.editor.on_key_hold(direction)
    
            # Soltar
            if self.game.input.is_key_released(key):
                self.editor.on_key_release(direction)

    
        # VELOCIDAD DE LAS NOTAS
        if self.game.input.is_key_pressed(pygame.K_LEFT):
            self.editor.remove_pixel_per_ms()

        elif self.game.input.is_key_held(pygame.K_LEFT):
            self.editor.remove_pixel_per_ms()

        if self.game.input.is_key_pressed(pygame.K_RIGHT):
            self.editor.add_pixel_per_ms()

        elif self.game.input.is_key_held(pygame.K_RIGHT):
            self.editor.add_pixel_per_ms()

        # CONTROLES
        if self.game.input.is_key_pressed(pygame.K_SPACE):
            self.editor.toggle_play_pause()
        
        if self.game.input.is_key_pressed(pygame.K_l):
            self.editor.toggle_loop()
        
        if self.game.input.is_key_pressed(pygame.K_RETURN):
            if self.editor.music.current_time:
                self.editor.close_section()
        
        if self.game.input.is_key_pressed(pygame.K_DELETE):
            self.editor.delete_section()
        
        if self.game.input.is_key_pressed(pygame.K_DOWN):
            self.editor.next_section()
        
        if self.game.input.is_key_pressed(pygame.K_UP):
            self.editor.previous_section()
            
        if self.game.input.is_key_pressed(pygame.K_BACKSPACE):
            self.editor.remove_last_note()
        
        if self.game.input.is_key_pressed(pygame.K_n):
            self.editor.toggle_snap()
        
        if self.game.input.is_key_pressed(pygame.K_ESCAPE):
            self.editor.export_to_json()
            self.game.state.change(StateID.MENU)
    
    def on_exit(self) -> None:
        self.editor.music.stop()
        super().on_exit()
    
    @property
    def overlay_type(self) -> OverlayType:
        return OverlayType.NONE
    
    @property
    def is_transient(self) -> bool:
        return False


