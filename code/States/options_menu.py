# IMPORTING LIBRARIES
import pygame
from os.path import join

# IMPORTING FILES
from settings import *
from Tools.data_loading_tools import save_data
from UI_elements.buttons import GenericButton, GenericToggleButton
from UI_elements.slider import Slider


# =========================================================
# BASE SECTION CLASS
# =========================================================
class OptionsSection:

    def __init__(s, game):

        s.game = game

        s.ui_elements = []
        s.selected_index = 0


    def handling_events(s, events):

        for element in s.ui_elements:
            element.handling_events(events)


    def update(s, dt):

        for element in s.ui_elements:
            element.update(dt)


    def draw(s, window, active):

        for i, element in enumerate(s.ui_elements):

            if hasattr(element, "is_selected"):
                element.is_selected = (active and i == s.selected_index)

            element.draw(window)


# =========================================================
# VIDEO SETTINGS
# =========================================================
class VideoSettings(OptionsSection):

    def __init__(s, game):

        super().__init__(game)
        s.setup()


    def setup(s):

        button_size = (240, 55)

        resolutions = [
            ("1920 x 1080", (1920, 1080)),
            ("1280 x 720", (1280, 720)),
            ("640 x 360", (640, 360)),
        ]

        y = 260

        for label, res in resolutions:

            btn = GenericButton(
                s.game,
                size=button_size,
                pos=(260, y),
                text=label,
                action=lambda r=res: s.change_resolution(r)
            )

            s.ui_elements.append(btn)

            y += 70


        fullscreen_button = GenericButton(
            s.game,
            size=button_size,
            pos=(260, y),
            text="Toggle Fullscreen",
            action=s.toggle_fullscreen
        )

        s.ui_elements.append(fullscreen_button)


    def change_resolution(s, res):

        width, height = res

        s.game.window_data["width"] = width
        s.game.window_data["height"] = height

        s.game.display = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE
        )

        save_data(s.game.window_data, WINDOW_DATA_PATH)


    def toggle_fullscreen(s):

        s.game.fullscreen = not s.game.fullscreen
        s.game.window_data["fullscreen"] = s.game.fullscreen

        if s.game.fullscreen:

            s.game.display = pygame.display.set_mode(
                (s.game.window_data["width"], s.game.window_data["height"]),
                pygame.FULLSCREEN
            )

        else:

            s.game.display = pygame.display.set_mode(
                (
                    s.game.window_data["width"],
                    s.game.window_data["height"]
                ),
                pygame.RESIZABLE
            )

        save_data(s.game.window_data, WINDOW_DATA_PATH)


# =========================================================
# AUDIO SETTINGS
# =========================================================
class AudioSettings(OptionsSection):

    def __init__(s, game):

        super().__init__(game)
        s.setup()


    def setup(s):

        music_slider = Slider(
            s.game,
            pos=(520, 270),
            size=(260, 16),
            min_val=0,
            max_val=1,
            start_val=s.game.audio_data.get("music_volume", 1.0),
            on_change=lambda v: s.game.audio_manager.set_music_volume(v)
        )

        sound_slider = Slider(
            s.game,
            pos=(520, 370),
            size=(260, 16),
            min_val=0,
            max_val=1,
            start_val=s.game.audio_data.get("sound_volume", 1.0),
            on_change=lambda v: s.game.audio_manager.set_sound_volume(v)
        )

        music_toggle = GenericToggleButton(
            s.game,
            size=(220, 50),
            pos=(520, 300),
            text="Music",
            action=s.game.audio_manager.toggle_music
        )

        sound_toggle = GenericToggleButton(
            s.game,
            size=(220, 50),
            pos=(520, 400),
            text="Sound",
            action=s.game.audio_manager.toggle_sound
        )

        s.ui_elements.extend([
            music_slider,
            music_toggle,
            sound_slider,
            sound_toggle
        ])


# =========================================================
# KEYBIND BUTTON
# =========================================================
class KeyBindButton:

    def __init__(s, game, action_name, key, pos):

        s.game = game
        s.action_name = action_name
        s.key = key

        s.waiting_for_key = False
        s.is_selected = False

        s.font = pygame.font.SysFont(None, 28)

        s.rect = pygame.Rect(pos[0], pos[1], 320, 50)


    def activate(s):
        s.waiting_for_key = True


    def handling_events(s, events):

        for event in events:

            if s.waiting_for_key and event.type == pygame.KEYDOWN:

                s.key = event.key
                s.waiting_for_key = False

                s.game.controls_data[s.action_name] = event.key

                save_data(
                    s.game.controls_data,
                    CONTROLLS_DATA_PATH
                )


    def update(s, dt):
        pass


    def draw(s, window):

        color = (90, 90, 90)

        if s.is_selected:
            color = (240, 210, 90)

        pygame.draw.rect(window, color, s.rect, border_radius=6)

        key_name = pygame.key.name(s.key)

        if s.waiting_for_key:
            key_name = "Press key..."

        text = f"{s.action_name} : {key_name}"

        surf = s.font.render(text, True, (20, 20, 20))

        window.blit(
            surf,
            (s.rect.x + 12, s.rect.y + 14)
        )


# =========================================================
# CONTROLS SETTINGS
# =========================================================
class ControlsSettings(OptionsSection):

    def __init__(s, game):

        super().__init__(game)
        s.setup()


    def setup(s):

        y = 260

        for action, key in s.game.controlls_data.items():

            btn = KeyBindButton(
                s.game,
                action,
                key,
                (880, y)
            )

            s.ui_elements.append(btn)

            y += 60


# =========================================================
# MAIN OPTIONS MENU
# =========================================================
class OptionsMenu:

    def __init__(s, game):

        s.game = game

        s.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        s.background.fill((25, 35, 55))

        s.panel = pygame.Surface((WINDOW_WIDTH - 200, WINDOW_HEIGHT - 200))
        s.panel.fill((45, 65, 95))

        s.panel_rect = s.panel.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))

        s.sections = [
            VideoSettings(game),
            AudioSettings(game),
            ControlsSettings(game)
        ]

        s.section_names = ["VIDEO", "AUDIO", "CONTROLS"]

        s.current_tab = 0
        s.nav_mode = "tabs"

        s.font = pygame.font.SysFont(None, 44)


    @property
    def current_section(s):
        return s.sections[s.current_tab]


    # =====================================================
    # INPUT
    # =====================================================
    def handling_events(s, events):

        for event in events:

            if event.type == pygame.KEYDOWN:

                # ======================
                # TAB NAVIGATION
                # ======================
                if s.nav_mode == "tabs":

                    if event.key == pygame.K_RIGHT:
                        s.current_tab = (s.current_tab + 1) % len(s.sections)

                    if event.key == pygame.K_LEFT:
                        s.current_tab = (s.current_tab - 1) % len(s.sections)

                    if event.key == pygame.K_DOWN:

                        if s.current_section.ui_elements:
                            s.nav_mode = "section"
                            s.current_section.selected_index = 0

                    if event.key == pygame.K_ESCAPE:
                        s.exit_menu()


                # ======================
                # SECTION NAVIGATION
                # ======================
                elif s.nav_mode == "section":

                    if event.key == pygame.K_DOWN:

                        s.current_section.selected_index += 1
                        s.current_section.selected_index %= len(
                            s.current_section.ui_elements
                        )

                    if event.key == pygame.K_UP:

                        if s.current_section.selected_index == 0:
                            s.nav_mode = "tabs"
                        else:
                            s.current_section.selected_index -= 1

                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):

                        element = s.current_section.ui_elements[
                            s.current_section.selected_index
                        ]

                        if hasattr(element, "activate"):
                            element.activate()

                    if event.key == pygame.K_ESCAPE:
                        s.nav_mode = "tabs"

        if s.nav_mode == "section":
            s.current_section.handling_events(events)


    # =====================================================
    # UPDATE
    # =====================================================
    def update(s, dt):

        s.current_section.update(dt)


    # =====================================================
    # DRAW
    # =====================================================
    def draw(s, window):

        window.blit(s.background, (0, 0))

        window.blit(s.panel, s.panel_rect)

        s.draw_tabs(window)

        s.current_section.draw(window, s.nav_mode == "section")

        s.draw_help(window)


    # =====================================================
    # DRAW TABS
    # =====================================================
    def draw_tabs(s, window):

        x = WINDOW_WIDTH//2 - 260
        y = 130
        spacing = 260

        for i, name in enumerate(s.section_names):

            color = (170,170,170)

            if i == s.current_tab:
                color = (255,220,100)

            text = s.font.render(name, True, color)

            window.blit(text, (x, y))

            if i == s.current_tab:

                pygame.draw.line(
                    window,
                    (255,220,100),
                    (x, y + 42),
                    (x + text.get_width(), y + 42),
                    4
                )

            x += spacing


    # =====================================================
    # HELP BAR
    # =====================================================
    def draw_help(s, window):

        font = pygame.font.SysFont(None, 26)

        if s.nav_mode == "tabs":
            text = "← → Change Tab    ↓ Open Settings    Esc Exit"
        else:
            text = "↑ ↓ Navigate    Enter Select    Esc Back"

        surf = font.render(text, True, (200,200,200))

        window.blit(
            surf,
            (WINDOW_WIDTH//2 - surf.get_width()//2, WINDOW_HEIGHT - 40)
        )


    # =====================================================
    # EXIT
    # =====================================================
    def exit_menu(s):

        if s.game.state_manager.last_state:
            s.game.state_manager.change_state(
                s.game.state_manager.last_state
            )