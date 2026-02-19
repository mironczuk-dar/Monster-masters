import pygame
from Tools.developer_tools import draw_fps_counter

class StateManager:
    def __init__(s, game):
        s.game = game
        s.states = {}
        s.current_state = None
        s.last_state = None

        # --- TRANSITION ATTRIBUTES ---
        s.transitioning = False
        s.transition_alpha = 0
        s.transition_speed = 1500
        s.next_state = None
        s.fading_out = True
        s.transition_color = (0, 0, 0)

        # --- POPUP GROUPS ---
        s.music_popups = pygame.sprite.Group()

    def add_state(s, name, state_object):
        s.states[name] = state_object

    def set_state(s, name):
        """Standard jump to state without transition."""
        if name in s.states:
            s.current_state = name
            s.game.audio_manager.play_for_state(name)
            
            state_obj = s.states[s.current_state]
            if hasattr(state_obj, 'on_enter'):
                state_obj.on_enter()

    def change_state(s, name):
        """RPG-style transition (Fade out -> Switch -> Fade in)."""
        if name in s.states and name != s.current_state:
            s.transitioning = True
            s.fading_out = True
            s.transition_alpha = 0
            s.next_state = name

    def handling_events(s, events):
        if s.transitioning and s.transition_alpha > 128:
            return
            
        if s.current_state:
            s.states[s.current_state].handling_events(events)

    def update(s, delta_time):
        s.music_popups.update(delta_time)

        if s.transitioning:
            s._handle_transition(delta_time)
        else:
            if s.current_state:
                s.states[s.current_state].update(delta_time)

    def draw(s, window):
        if s.current_state:
            s.states[s.current_state].draw(window)

        if s.transitioning or s.transition_alpha > 0:
            overlay = pygame.Surface(window.get_size())
            overlay.fill(s.transition_color)
            overlay.set_alpha(int(s.transition_alpha))
            window.blit(overlay, (0, 0))

        for popup in s.music_popups:
            popup.draw(window)

        draw_fps_counter(s.game, (s.game.window.get_width() - 150, 15))

    def _handle_transition(s, delta_time):
        if s.fading_out:
            s.transition_alpha += s.transition_speed * delta_time
            if s.transition_alpha >= 255:
                s.transition_alpha = 255
                s.last_state = s.current_state
                s.set_state(s.next_state)
                s.fading_out = False
        else:
            s.transition_alpha -= s.transition_speed * delta_time
            if s.transition_alpha <= 0:
                s.transition_alpha = 0
                s.transitioning = False