# IMPORTING LIBRARIES
import pygame
from os.path import join

# IMPORTING FILES
from settings import *
from Tools.data_loading_tools import save_data
from UI_elements.buttons import GenericButton, GenericToggleButton
from UI_elements.slider import Slider

#IMPORTING DATA
from Manifest.music_track_manifest import OVERWORLD_MUSIC_TRACKS


class OptionsSection:

    def __init__(s, game):

        s.game = game

        s.ui_elements = []
        s.selected_index = 0


    def handling_events(s, events):

        for element in s.ui_elements:
            if element:
                element.handling_events(events)


    def update(s, dt):

        for element in s.ui_elements:
            element.update(dt)


    def draw(s, window, active):

        for i, element in enumerate(s.ui_elements):

            if hasattr(element, "is_selected"):
                element.is_selected = (active and i == s.selected_index)

            element.draw(window)

class VideoSettings(OptionsSection):

    def __init__(s, game, menu):
        super().__init__(game)
        s.menu = menu
        s.fps_options = [90, 60, 40, 30]
        s.setup()


    def setup(s):

        button_size = (320, 65)
        column_offset = 200

        center_x = s.menu.panel_rect.centerx
        top_y = s.menu.panel_rect.top + 100

        left_x = center_x - column_offset
        right_x = center_x + column_offset

        spacing_y = 80

        # ---- HEADERS ----
        s.header_font = pygame.font.SysFont("Arial", 30, bold=True)
        s.headers = [
            ("FRAMERATE", (left_x, top_y - 50)),
            ("RESOLUTION", (right_x, top_y - 50))
        ]

        # ---- RESOLUTION OPTIONS ----
        resolutions = [
            ("1920 x 1080", (1920, 1080)),
            ("1280 x 720", (1280, 720)),
            ("960 x 540", (960, 540)),
            ("640 x 360", (640, 360)),
        ]

        # ---- GRID ROWS (FPS | RESOLUTION) ----
        y = top_y

        for fps, (label, res) in zip(s.fps_options, resolutions):

            fps_btn = GenericButton(
                s.game,
                size=button_size,
                pos=(left_x, y),
                text=f"{fps} FPS",
                colour=(60, 75, 100),
                text_colour=(220, 230, 240),
                action=lambda f=fps: s.update_fps(f)
            )

            res_btn = GenericButton(
                s.game,
                size=button_size,
                pos=(right_x, y),
                text=label,
                colour=(60, 75, 100),
                text_colour=(220, 230, 240),
                action=lambda r=res: s.change_resolution(r)
            )

            s.ui_elements.append(fps_btn)
            s.ui_elements.append(res_btn)

            y += spacing_y


        # ---- SYSTEM ROW (FULLSCREEN | SHOW FPS) ----
        bottom_y = s.menu.panel_rect.bottom - 80

        fullscreen_btn = GenericButton(
            s.game,
            size=button_size,
            pos=(right_x, bottom_y),
            text="Fullscreen Mode",
            colour=(80, 60, 100),
            text_colour=(255, 255, 255),
            action=s.toggle_fullscreen
        )

        show_fps_toggle = GenericToggleButton(
            s.game,
            size=button_size,
            pos=(left_x, bottom_y),
            text="Show FPS Counter",
            active_colour=(40, 120, 80),
            inactive_colour=(120, 60, 60),
            action=s.toggle_show_fps
        )

        show_fps_toggle.is_on = s.game.window_data.get("show_fps", False)
        show_fps_toggle.update_appearance()

        s.ui_elements.append(show_fps_toggle)
        s.ui_elements.append(fullscreen_btn)

        # ilość kolumn dla nawigacji
        s.columns = 2


    def draw(s, window, active):

        for text, pos in s.headers:
            surf = s.header_font.render(text, True, (150, 160, 180))
            rect = surf.get_rect(center=pos)
            window.blit(surf, rect)

        super().draw(window, active)


    # ---- LOGIC ----

    def update_fps(s, new_fps):

        s.game.fps = new_fps
        s.game.window_data["fps"] = new_fps

        save_data(
            s.game.window_data,
            WINDOW_DATA_PATH
        )


    def toggle_show_fps(s):

        state = not s.game.window_data.get("show_fps", False)

        s.game.window_data["show_fps"] = state

        save_data(
            s.game.window_data,
            WINDOW_DATA_PATH
        )


    def change_resolution(s, res):

        width, height = res

        s.game.window_data["width"] = width
        s.game.window_data["height"] = height

        s.game.display = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE
        )

        save_data(
            s.game.window_data,
            WINDOW_DATA_PATH
        )


    def toggle_fullscreen(s):

        s.game.fullscreen = not s.game.fullscreen

        s.game.window_data["fullscreen"] = s.game.fullscreen

        flags = pygame.FULLSCREEN if s.game.fullscreen else pygame.RESIZABLE

        s.game.display = pygame.display.set_mode(
            (
                s.game.window_data["width"],
                s.game.window_data["height"]
            ),
            flags
        )

        save_data(
            s.game.window_data,
            WINDOW_DATA_PATH
        )

class AudioSettings(OptionsSection):

    def __init__(s, game):

        super().__init__(game)
        s.setup()


    def setup(s):

        slider_size = (800, 40)
        music_slider = Slider(
            s.game,
            pos=(WINDOW_WIDTH/2-slider_size[0]/2, WINDOW_HEIGHT/3),
            size=slider_size,
            min_val=0,
            max_val=1,
            start_val=s.game.audio_data.get("music_volume", 1.0),
            on_change=lambda v: s.game.audio_manager.set_music_volume(v)
        )

        sound_slider = Slider(
            s.game,
            pos=(WINDOW_WIDTH/2-slider_size[0]/2, WINDOW_HEIGHT/3*2),
            size=(slider_size),
            min_val=0,
            max_val=1,
            start_val=s.game.audio_data.get("sound_volume", 1.0),
            on_change=lambda v: s.game.audio_manager.set_sound_volume(v)
        )

        music_toggle = GenericToggleButton(
            s.game,
            size=(220, 50),
            pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT/3+slider_size[1]+50),
            text="Music",
            action=s.game.audio_manager.toggle_music
        )

        sound_toggle = GenericToggleButton(
            s.game,
            size=(220, 50),
            pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT/3*2+slider_size[1]+50),
            text="Sound",
            action=s.game.audio_manager.toggle_sound
        )

        s.ui_elements.extend([
            music_slider,
            music_toggle,
            sound_slider,
            sound_toggle
        ])

class KeyBindButton:

    def __init__(s, game, action_name, key, pos):

        s.game = game
        s.action_name = action_name

        s.waiting_for_key = False
        s.is_selected = False

        s.font = pygame.font.SysFont("Arial", 26)

        s.rect = pygame.Rect(pos[0], pos[1], 360, 55)


    def activate(s):
        s.waiting_for_key = True


    def handling_events(s, events):

        if not s.waiting_for_key:
            return

        for event in events:

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                s.waiting_for_key = False
                return

            new_key = event.key

            # sprawdzamy czy klawisz jest już używany
            for action, key in s.game.controlls_data.items():

                if key == new_key:

                    # zamieniamy klawisze miejscami
                    old_key = s.game.controlls_data[s.action_name]
                    s.game.controlls_data[action] = old_key
                    break

            # ustawiamy nowy klawisz
            s.game.controlls_data[s.action_name] = new_key

            save_data(
                s.game.controlls_data,
                CONTROLLS_DATA_PATH
            )

            s.waiting_for_key = False
            return
            


    def update(s, dt):
        pass


    def draw(s, window):

        bg = (70, 80, 100)

        if s.is_selected:
            bg = (240, 210, 90)

        pygame.draw.rect(window, bg, s.rect, border_radius=8)

        action_text = s.font.render(
            s.action_name.replace("_", " ").title(),
            True,
            (20, 20, 20)
        )

        window.blit(
            action_text,
            (s.rect.x + 14, s.rect.centery - action_text.get_height() // 2)
        )

        if s.waiting_for_key:
            key_name = "PRESS KEY..."
        else:
            key_code = s.game.controlls_data[s.action_name]
            key_name = pygame.key.name(key_code).upper()

        key_text = s.font.render(
            key_name,
            True,
            (20, 20, 20)
        )

        key_rect = key_text.get_rect(
            midright=(s.rect.right - 14, s.rect.centery)
        )

        window.blit(key_text, key_rect)

class ControlsSettings(OptionsSection):

    def __init__(s, game):

        super().__init__(game)
        s.setup()


    def setup(s):

        spacing_x = 420
        spacing_y = 70

        start_x = WINDOW_WIDTH // 2 - spacing_x // 2
        start_y = 260

        left_actions = [
            "action_a",
            "action_b",
            "options"
        ]

        right_actions = [
            "up",
            "down",
            "left",
            "right"
        ]

        max_rows = max(len(left_actions), len(right_actions))

        for row in range(max_rows):

            if row < len(left_actions):

                action = left_actions[row]
                key = s.game.controlls_data[action]

                btn = KeyBindButton(
                    s.game,
                    action,
                    key,
                    (start_x, start_y + row * spacing_y)
                )

                s.ui_elements.append(btn)

            else:
                s.ui_elements.append(None)


            if row < len(right_actions):

                action = right_actions[row]
                key = s.game.controlls_data[action]

                btn = KeyBindButton(
                    s.game,
                    action,
                    key,
                    (start_x + spacing_x, start_y + row * spacing_y)
                )

                s.ui_elements.append(btn)

        s.columns = 2


    def handling_events(s, events):

        for element in s.ui_elements:
            if element:
                element.handling_events(events)

    def is_waiting_for_key(s):
        for element in s.ui_elements:
            if element and getattr(element, "waiting_for_key", False):
                return True
        return False


    def update(s, dt):

        for element in s.ui_elements:
            if element:
                element.update(dt)


    def draw(s, window, active):

        for i, element in enumerate(s.ui_elements):

            if element is None:
                continue

            element.is_selected = (active and i == s.selected_index)

            element.draw(window)

class OptionsMenu:
    def __init__(s, game):
        s.game = game

        # --- WYGLĄD ---
        s.bg_color = (20, 25, 35)      
        s.panel_color = (40, 50, 65)   
        s.accent_color = (255, 200, 70) 
        s.border_color = (60, 80, 110)

        # Definicja wymiarów panelu
        s.panel_width = WINDOW_WIDTH - 150
        s.panel_height = WINDOW_HEIGHT - 180
        s.panel_rect = pygame.Rect(0, 0, s.panel_width, s.panel_height)
        s.panel_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)

        # Powierzchnia panelu (opcjonalnie dla optymalizacji)
        s.panel_surf = pygame.Surface((s.panel_width, s.panel_height), pygame.SRCALPHA)

        # --- SEKCJE ---
        # UWAGA: Wszystkie sekcje teraz muszą przyjmować (game, menu) w __init__
        s.sections = [
            VideoSettings(game, s), 
            AudioSettings(game),    # Upewnij się, że poprawiłeś __init__ w tych klasach!
            ControlsSettings(game)
        ]

        s.section_names = ["VIDEO", "AUDIO", "CONTROLS"]
        s.current_tab = 0
        s.nav_mode = "tabs"
        s.font = pygame.font.SysFont("Arial", 40, bold=True)

        s.back_button = GenericButton(
            game,
            size=(140, 50),
            pos=(80, 60),
            text="BACK",
            colour=(120, 60, 60),
            text_colour=(255, 255, 255),
            action=s.exit_menu
        )

        s.back_selected = False

    # =====================================================
    # FIX: Dodajemy brakujące property
    # =====================================================
    @property
    def current_section(s):
        return s.sections[s.current_tab]

    def handling_events(s, events):

        ctrl = s.game.controlls_data
        section = s.current_section

        # jeśli czekamy na keybind → NIE nawigujemy menu
        if isinstance(section, ControlsSettings) and section.is_waiting_for_key():
            section.handling_events(events)
            return

        for event in events:

            if event.type != pygame.KEYDOWN:
                continue

            # ---------------- TABS ----------------
            if s.nav_mode == "tabs":

                if event.key == ctrl["left"]:
                    s.current_tab = (s.current_tab - 1) % len(s.sections)

                elif event.key == ctrl["right"]:
                    s.current_tab = (s.current_tab + 1) % len(s.sections)

                elif event.key == ctrl["down"]:
                    if section.ui_elements:
                        s.nav_mode = "section"
                        section.selected_index = 0

                elif event.key == ctrl["up"]:
                    s.nav_mode = "back"

                elif event.key == ctrl["action_b"]:
                    s.exit_menu()

            # ---------------- BACK BUTTON ----------------
            elif s.nav_mode == "back":

                if event.key == ctrl["down"]:
                    s.nav_mode = "tabs"

                elif event.key == ctrl["action_a"]:
                    s.back_button.activate()

            # ---------------- SECTION ----------------
            elif s.nav_mode == "section":

                if event.key == ctrl["action_b"]:
                    s.nav_mode = "tabs"
                    return

                index = section.selected_index
                total = len(section.ui_elements)
                columns = getattr(section, "columns", 1)

                if event.key == ctrl["down"]:
                    index += columns
                    if index >= total:
                        index = index % columns
                    section.selected_index = index

                elif event.key == ctrl["up"]:
                    index -= columns
                    if index < 0:
                        s.nav_mode = "tabs"
                    else:
                        section.selected_index = index

                elif event.key == ctrl["right"] and columns > 1:
                    if (index % columns) < columns - 1 and index + 1 < total:
                        section.selected_index += 1

                elif event.key == ctrl["left"] and columns > 1:
                    if (index % columns) > 0:
                        section.selected_index -= 1

                elif event.key == ctrl["action_a"]:
                    element = section.ui_elements[section.selected_index]
                    if element and hasattr(element, "activate"):
                        element.activate()

        # przekazanie eventów dalej
        if s.nav_mode == "section":
            section.handling_events(events)

        if s.nav_mode == "back":
            s.back_button.handling_events(events)

    def update(s, dt):
        s.current_section.update(dt)
        s.back_button.update(dt)

    def draw(s, window):
        # 1. Tło
        window.fill(s.bg_color)

        # draw back button
        s.back_button.is_selected = (s.nav_mode == "back")
        s.back_button.draw(window)

        # 2. Rysowanie panelu (Cień + Panel + Ramka)
        shadow_rect = s.panel_rect.copy()
        shadow_rect.move_ip(8, 8)
        pygame.draw.rect(window, (10, 10, 15, 150), shadow_rect, border_radius=20)
        pygame.draw.rect(window, s.panel_color, s.panel_rect, border_radius=20)
        pygame.draw.rect(window, s.border_color, s.panel_rect, width=3, border_radius=20)

        s.draw_tabs(window)
        
        # FIX: Wywołanie aktualnej sekcji
        s.current_section.draw(window, s.nav_mode == "section")
        
        s.draw_help(window)

    def draw_tabs(s, window):
        # dynamiczne centrowanie tabów
        tab_spacing = 250
        start_x = WINDOW_WIDTH // 2 - ((len(s.sections) - 1) * tab_spacing) // 2
        y = s.panel_rect.top - 60

        for i, name in enumerate(s.section_names):
            is_active = (i == s.current_tab)
            color = s.accent_color if is_active else (130, 140, 160)
            
            # Jeśli jesteśmy w trybie "tabs", podświetlamy taba mocniej
            if is_active and s.nav_mode == "tabs":
                color = (255, 255, 255) # Biały gdy nawigujemy po tabach

            text_surf = s.font.render(name, True, color)
            text_rect = text_surf.get_rect(center=(start_x + i * tab_spacing, y))
            
            if is_active:
                # Linia pod aktywnym tabem
                line_w = text_rect.width + 20
                pygame.draw.rect(window, s.accent_color, (text_rect.centerx - line_w//2, text_rect.bottom + 5, line_w, 4), border_radius=2)

            window.blit(text_surf, text_rect)

    def draw_help(s, window):
        help_font = pygame.font.SysFont("Arial", 22)
        if s.nav_mode == "tabs":
            txt = "← → Change Tab  |  ↓ Enter Section  |  ESC Close"
        else:
            txt = "↑ ↓ Navigate  |  ENTER Select  |  ESC Back to Tabs"
        
        surf = help_font.render(txt, True, (100, 110, 130))
        window.blit(surf, (WINDOW_WIDTH//2 - surf.get_width()//2, WINDOW_HEIGHT - 45))

    def exit_menu(s):
        if s.game.state_manager.last_state:

            if s.game.state_manager.last_state == "Singleplayer":

                state = s.game.state_manager.states["Singleplayer"]

                map_name = state.world.current_map_name

                s.game.audio_manager.play_music(
                    OVERWORLD_MUSIC_TRACKS.get(
                        map_name,
                        "World map tune"
                    )
                )

            s.game.state_manager.change_state(
                s.game.state_manager.last_state
            )

    def get_next_valid_index(s, index):
        total = len(s.ui_elements)

        while 0 <= index < total and s.ui_elements[index] is None:
            index += 1

        return index