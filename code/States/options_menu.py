# IMPORTING LIBRARIES
import pygame
from os.path import join

# IMPORTING FILES
from settings import *
from Tools.data_loading_tools import save_data
from UI_elements.buttons import GenericButton, ToggleButton
from UI_elements.slider import Slider
from UI_elements.options_ui.FPS_preview_ball import Ball


# ================================
# OPTIONS MENU
# ================================
class OptionsMenu:

    def __init__(s, game):
        s.game = game

        # BACKGROUND
        s.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        s.background.fill((40, 60, 90))

        # FPS PREVIEW OBJECT
        s.fps_preview_ball = Ball((WINDOW_WIDTH - 400, WINDOW_HEIGHT - 100), (255, 0, 0))

        # UI ELEMENT STORAGE
        s.buttons = []
        s.toggles = []
        s.sliders = []

        # OPTIONS
        s.fps_options = [90, 60, 40, 30]

        # PREVIEW SOUND
        s.test_sound = pygame.mixer.Sound(
            join(BASE_DIR, 'audio', 'Sound effects', 'scratch.mp3')
        )

        # BUILD UI
        s.setup()

    # ================================
    # UI SETUP
    # ================================
    def setup(s):

        button_size = (220, 55)
        spacing = 12

        left_x = 180
        middle_x = 460
        right_x = 760

        y_start = 180

        # ----- BACK BUTTON -----
        s.buttons.append(
            GenericButton(
                s.game,
                size=(180, 50),
                pos=(110, 40),
                text="<< Back",
                action=lambda: s.game.state_manager.change_state(
                    s.game.state_manager.last_state
                )
            )
        )

        # ----- SHOW FPS TOGGLE -----
        s.show_fps_toggle = ToggleButton(
            s.game,
            size=(180, 50),
            pos=(320, 40),
            text="Show FPS",
            action=s.toggle_show_fps
        )

        s.show_fps_toggle.is_on = s.game.window_data.get("show_fps", False)
        s.update_fps_toggle_text()
        s.toggles.append(s.show_fps_toggle)

        # ========================
        # LEFT COLUMN - RESOLUTION
        # ========================
        resolutions = [
            ("Fullscreen", None),
            ("1920x1080", (1920, 1080)),
            ("1280x720", (1280, 720)),
            ("640x360", (640, 360)),
        ]

        y = y_start
        for label, res in resolutions:

            if res is None:
                action = s.go_fullscreen
            else:
                action = lambda r=res: s.change_resolution(r[0], r[1])

            s.buttons.append(
                GenericButton(
                    s.game,
                    size=button_size,
                    pos=(left_x, y),
                    text=label,
                    action=action
                )
            )

            y += button_size[1] + spacing

        # ========================
        # MIDDLE COLUMN - FPS
        # ========================
        y = y_start
        for fps in s.fps_options:

            s.buttons.append(
                GenericButton(
                    s.game,
                    size=button_size,
                    pos=(middle_x, y),
                    text=f"{fps} FPS",
                    action=lambda f=fps: s.update_fps(f)
                )
            )

            y += button_size[1] + spacing

        # ========================
        # RIGHT COLUMN - AUDIO
        # ========================
        music_start = s.game.audio_data.get("music_volume", 1.0)
        sound_start = s.game.audio_data.get("sound_volume", 1.0)

        # MUSIC SLIDER
        s.music_slider = Slider(
            s.game,
            pos=(right_x - 110, y_start),
            size=(220, 16),
            min_val=0,
            max_val=1,
            start_val=music_start,
            on_change=lambda v: s.game.audio_manager.set_music_volume(v)
        )
        s.sliders.append(s.music_slider)

        # SOUND SLIDER
        s.sound_slider = Slider(
            s.game,
            pos=(right_x - 110, y_start + 90),
            size=(220, 16),
            min_val=0,
            max_val=1,
            start_val=sound_start,
            on_change=lambda v: s.game.audio_manager.set_sound_volume(v)
        )
        s.sliders.append(s.sound_slider)

        # MUSIC TOGGLE
        music_toggle = ToggleButton(
            s.game,
            size=(180, 50),
            pos=(right_x, y_start + 40),
            text="Music",
            action=s.game.audio_manager.toggle_music
        )
        music_toggle.is_on = s.game.audio_data.get("music_on", True)
        music_toggle.update_appearance()
        s.toggles.append(music_toggle)

        # SOUND TOGGLE
        sound_toggle = ToggleButton(
            s.game,
            size=(180, 50),
            pos=(right_x, y_start + 130),
            text="Sound",
            action=s.game.audio_manager.toggle_sound
        )
        sound_toggle.is_on = s.game.audio_data.get("sound_on", True)
        sound_toggle.update_appearance()
        s.toggles.append(sound_toggle)

    # ================================
    # HELPERS
    # ================================
    def update_fps_toggle_text(s):
        if s.show_fps_toggle.is_on:
            s.show_fps_toggle.text = "Hide FPS"
        else:
            s.show_fps_toggle.text = "Show FPS"
        s.show_fps_toggle.update_appearance()

    # ================================
    # STATE LOOP
    # ================================
    def handling_events(s, events):

        for b in s.buttons:
            b.handling_events(events)

        for t in s.toggles:
            t.handling_events(events)

        for sl in s.sliders:
            sl.handling_events(events)

    def update(s, delta_time):

        for b in s.buttons:
            b.update(delta_time)

        for t in s.toggles:
            t.update(delta_time)

        for sl in s.sliders:
            sl.update(delta_time)

        s.fps_preview_ball.update(delta_time)

    def draw(s, window):

        window.blit(s.background, (0, 0))

        for b in s.buttons:
            b.draw(window)

        for t in s.toggles:
            t.draw(window)

        for sl in s.sliders:
            sl.draw(window)

        s.fps_preview_ball.draw(window)

    # ================================
    # OPTIONS LOGIC
    # ================================
    def change_resolution(s, width, height):

        s.game.window_data["width"] = width
        s.game.window_data["height"] = height

        s.game.display = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE
        )

        save_data(s.game.window_data, WINDOW_DATA_PATH)

    def go_fullscreen(s):

        s.game.fullscreen = not s.game.fullscreen
        s.game.window_data["fullscreen"] = s.game.fullscreen

        if s.game.fullscreen:
            s.game.last_window_size = (
                s.game.display.get_width(),
                s.game.display.get_height()
            )
            s.game.display = pygame.display.set_mode(
                (s.game.window_data["width"], s.game.window_data["height"]),
                pygame.FULLSCREEN
            )
        else:
            s.game.display = pygame.display.set_mode(
                s.game.last_window_size,
                pygame.RESIZABLE
            )

        save_data(s.game.window_data, WINDOW_DATA_PATH)

    def update_fps(s, new_fps):

        s.game.fps = new_fps
        s.game.window_data["fps"] = new_fps

        save_data(s.game.window_data, WINDOW_DATA_PATH)

    def toggle_show_fps(s):

        s.game.window_data["show_fps"] = s.show_fps_toggle.is_on
        save_data(s.game.window_data, WINDOW_DATA_PATH)

        s.update_fps_toggle_text()