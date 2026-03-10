# IMPORTING LIBRARIES
import pygame
import sys
from random import choice
from os.path import join

# IMPORTING FILES
from States.generic_state import BaseState
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, BASE_DIR
from UI_elements.buttons import GenericButton, ImageAudioButton

#IMPORTING FUNCTIONS FOR LOADING ASSETS
from Tools.game_elemet_importing_machine import monster_asset_importer, scale_asset, import_image
from Tools.text_formating_tools import create_text_with_outline

#IMPORTING AUDIO MANAGER
from Managers.audio_manager import AudioManager


#STARTER MENU CLASS
class StartMenu(BaseState):
    def __init__(s, game):
        super().__init__(game)

        # ANIMATION
        s.monster_frames = []
        s.frame_index = 0
        s.animation_speed = 6
        s.monster_pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        # UI
        s.background = None
        s.font = pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 40)
        s.buttons = []

        # KEYBOARD NAVIGATION
        s.active_index = 0

        # MONSTER MAP
        s.monster_map = {
            1: 'Pluma',
            2: 'Friolera',
            3: 'Finiette'
        }

        # VERSION TEXT
        s.version_surface = create_text_with_outline(
            'Version: ALPHA 1.0.0',
            s.font,
            (255,255,255),
            (0,0,0),
            4
        )

        s.setup()

    #METHOD THAT RUNS EVERY TIME WE ENTER THE MENU
    def on_enter(s):
        bg_id = choice([1, 2, 3])
        bg_name = f'background_{bg_id}'
        monster_name = s.monster_map.get(bg_id, 'Pluma')

        try:
            bg_path = join(BASE_DIR, 'assets', 'start_menu_assets', 'start_menu_backgrounds', f'{bg_name}.png')
            raw_bg = pygame.image.load(bg_path).convert()
            s.background = pygame.transform.scale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))

            monster_data = monster_asset_importer(
                4, 2, 
                BASE_DIR, 'assets', 'monsters', 
                target_monster=monster_name
            )

            if monster_name in monster_data:
                s.monster_frames = monster_data[monster_name]['idle']
                s.monster_frames = scale_asset(s.monster_frames, 3)
                s.frame_index = 0
                
                m_width = s.monster_frames[0].get_width()
                m_height = s.monster_frames[0].get_height()
                s.monster_pos = (
                    WINDOW_WIDTH * 0.7 - m_width // 2,
                    WINDOW_HEIGHT * 0.6 - m_height // 2
                )


            monster_cry = s.game.start_menu_monster_cries.get(monster_name)
            
            for btn in s.buttons:
                if hasattr(btn, 'waiting_for_audio'):
                    btn.waiting_for_audio = False
                    btn.sound = None

            if len(s.buttons) > 0:
                s.buttons[0].wait_for_sound_to_end = True
                s.buttons[0].sound = monster_cry
            
        except Exception as e:
            print(f"Error in StartMenu.on_enter: {e}")
            s.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            s.background.fill('#ADD8E6')

    #METHOD FOR UPDATING THE MENU (ANIMATIONS, BUTTONS, ...)
    def update(s, delta_time):

        for i, button in enumerate(s.buttons):
            button.is_selected = (i == s.active_index)
            button.update(delta_time)

        if s.monster_frames:
            s.frame_index += s.animation_speed * delta_time
            if s.frame_index >= len(s.monster_frames):
                s.frame_index = 0

    #METHOD FOR HANDLING EVENTS IN THE MENU (BUTTON CLICKS, ...)
    def handling_events(s, events):
        mouse_pos = s.game.get_scaled_mouse_pos()
        ctrl = s.game.controlls_data
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                
                #NAVIGATING THE KEYBOARD GRID
                if event.key == ctrl['up']:
                    s.active_index = (s.active_index - 1) % len(s.buttons)

                elif event.key == ctrl['down']:
                    s.active_index = (s.active_index + 1) % len(s.buttons)

                elif event.key == ctrl['action_a']:
                    s.buttons[s.active_index].press()

        # HOVER MYSZY
        for i, button in enumerate(s.buttons):
            if button.rect.collidepoint(mouse_pos):
                s.active_index = i

        # SYNCHRONIZACJA SELECTED
        for i, button in enumerate(s.buttons):
            button.is_selected = (i == s.active_index)

        # przekazanie eventów do przycisków
        for button in s.buttons:
            button.handling_events(events)

    #METHOD FOR DRAWING THE START MENU
    def draw(s, window):
        if s.background:
            window.blit(s.background, (0, 0))

        if s.monster_frames:
            current_frame = s.monster_frames[int(s.frame_index)]
            window.blit(current_frame, s.monster_pos)

        window.blit(s.version_surface, (
            WINDOW_WIDTH - s.version_surface.get_width() - 10,
            WINDOW_HEIGHT - s.version_surface.get_height() - 10
        ))

        for button in s.buttons:
            button.draw(window)

    #METHOD FOR SETTING UP THE MENU (CREATING BUTTONS, ...)
    def setup(s):
        button_width = 450
        pos_x = button_width // 2 + 50 
        pos_y = 80
        visible_states = ["Singleplayer menu", "Options menu"]
        button_image = import_image(BASE_DIR, 'assets', 'start_menu_assets', 'start_menu_buttons', 'orange_button')
        hovered_button_image = import_image(BASE_DIR, 'assets', 'start_menu_assets', 'start_menu_buttons', 'blue_button')

        scale_ratio = button_width / button_image.get_width()
        button_image = pygame.transform.scale_by(button_image, scale_ratio)
        hovered_button_image = pygame.transform.scale_by(hovered_button_image, scale_ratio)

        for key in visible_states:
            btn = ImageAudioButton(
                s.game,
                (pos_x, pos_y),
                button_image,
                hovered_button_image,
                text=key.replace("menu", "").strip(),
                action=lambda k=key: s.game.state_manager.change_state(k),
                sound=None,
                text_size=50,
                font=join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'))
            s.buttons.append(btn)
            pos_y += button_image.get_height() + 10

        s.buttons.append(ImageAudioButton(
                s.game,
                (pos_x, pos_y),
                button_image,
                hovered_button_image,
                text="Exit Game",
                action=s.exit_game,
                sound=None,
                text_size=50,
                font=join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf')))

    def exit_game(s):
        s.game.save()
        pygame.quit()
        sys.exit()