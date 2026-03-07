# IMPORTING LIBRARIES
import pygame
import sys
from random import choice
from os.path import join

# IMPORTING FILES
from States.generic_state import BaseState
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, BASE_DIR
from UI_elements.buttons import GenericButton, AudioButton

#IMPORTING FUNCTIONS FOR LOADING ASSETS
from Tools.game_elemet_importing_machine import monster_asset_importer, scale_asset
from Tools.text_formating_tools import create_text_with_outline

#IMPORTING AUDIO MANAGER
from Managers.audio_manager import AudioManager


#STARTER MENU CLASS
class StartMenu(BaseState):
    def __init__(s, game):
        super().__init__(game)
        
        #ANIMATION ATTRIBUTES
        s.monster_frames = []
        s.frame_index = 0
        s.animation_speed = 6
        s.monster_pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        #UI ELEMENTS
        s.background = None
        s.font = pygame.font.SysFont(None, 40)
        s.buttons = []
        
        #MONSTER / BACKGROUND CHOICE
        s.monster_map = {
            1: 'Pluma',
            2: 'Friolera',
            3: 'Finiette'
        }

        #VERSION INFORMATION
        s.version_surface = create_text_with_outline(
        'Version: ALPHA 1.0.0', 
        s.font, 
        (255, 255, 255), 
        (0, 0, 0), 
        4)

        s.setup()

    #METHOD THAT RUNS EVERY TIME WE ENTER THE MENU
    def on_enter(s):

        #BACKGROUND AND MONSTER SELECTION
        bg_id = choice([1, 2, 3])
        bg_name = f'background_{bg_id}'
        monster_name = s.monster_map.get(bg_id, 'Pluma')

        try:
            #BACKGROUND
            bg_path = join(BASE_DIR, 'assets', 'start_menu_backgrounds', f'{bg_name}.png')
            raw_bg = pygame.image.load(bg_path).convert()
            s.background = pygame.transform.scale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))

            #IMPORTING THE MONSTER ASSETS
            monster_data = monster_asset_importer(
                4, 2, 
                BASE_DIR, 'assets', 'monsters', 
                target_monster=monster_name
            )

            #MONSTER FRAMES
            if monster_name in monster_data:
                s.monster_frames = monster_data[monster_name]['idle']
                s.monster_frames = scale_asset(s.monster_frames, 3)
                s.frame_index = 0
                
                #MONSTER POSITION
                m_width = s.monster_frames[0].get_width()
                m_height = s.monster_frames[0].get_height()
                s.monster_pos = (
                    WINDOW_WIDTH * 0.7 - m_width // 2,
                    WINDOW_HEIGHT * 0.6 - m_height // 2
                )

            s.buttons[0].sound = s.game.start_menu_monster_cries[f'{monster_name}']
            
        except Exception as e:
            print(f"Error: {e}")
            s.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            s.background.fill('#ADD8E6')

    #METHOD FOR UPDATING THE MENU (ANIMATIONS, BUTTONS, ...)
    def update(s, delta_time):
        for button in s.buttons:
            button.update(delta_time)

        #UPDATING THE MONSTER ANIMATION FRAME
        if s.monster_frames:
            s.frame_index += s.animation_speed * delta_time
            if s.frame_index >= len(s.monster_frames):
                s.frame_index = 0

    #METHOD FOR HANDLING EVENTS IN THE MENU (BUTTON CLICKS, ...)
    def handling_events(s, events):
        for button in s.buttons:
            button.handling_events(events)

    #METHOD FOR DRAWING THE START MENU
    def draw(s, window):

        if s.background:
            window.blit(s.background, (0, 0))

        if s.monster_frames:
            current_frame = s.monster_frames[int(s.frame_index)]
            window.blit(current_frame, s.monster_pos)

        #DRAWING THE VERSION TEXT WITH OUTLINE
        window.blit(s.version_surface, (
        WINDOW_WIDTH - s.version_surface.get_width() - 10,
        WINDOW_HEIGHT - s.version_surface.get_height() - 10
        ))

        for button in s.buttons:
            button.draw(window)

    #METHOD FOR SETTING UP THE MENU (CREATING BUTTONS, ...)
    def setup(s):
        size = (250, 80)
        pos_x = 130 
        pos_y = 80
        visible_states = ["Singleplayer menu", "Options menu"]

        for key in visible_states:
            if key == 'Singleplayer menu':
                btn = AudioButton(
                    s.game,
                    size,
                    (pos_x, pos_y),
                    key,
                    action = lambda k = key: s.game.state_manager.change_state(k),
                    sound = None
                )
            else:
                btn = GenericButton(
                    s.game,
                    size,
                    (pos_x, pos_y),
                    key,
                    action = lambda k = key: s.game.state_manager.change_state(k)
                )
            s.buttons.append(btn)
            pos_y += size[1] + 10

        s.buttons.append(GenericButton(
            s.game, size, (pos_x, pos_y), "Exit Game", action=s.exit_game
        ))

    def exit_game(s):
        s.game.save()
        pygame.quit()
        sys.exit()