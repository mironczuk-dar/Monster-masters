#IMPORTING LIBRARIES
import pygame
from sys import exit
from os import environ
import threading

#IMPORTING FILES
from settings import *
from Tools.data_loading_tools import load_data, save_data

#IMPORTING GAME MANAGERS
from Managers.state_manager import StateManager
from Managers.audio_manager import AudioManager

#IMPROTING STATES
from States.start_menu import StartMenu
from States.options_menu import OptionsMenu
from States.singleplayer_menu import SingleplayerMenu
from States.new_save_wizzard import NewSaveWizard

#IMPROTING FUNCTIONS FOR LOADING ASSETS
from Tools.game_elemet_importing_machine import (
    load_maps,
    load_audio_assets,
    load_assets,
    load_game_fonts
)

#LAUNCHER CLASS
class Game:

    #INFORMATION ABOUT THE LAUNCHER
    def __str__(s):
        return'''
        A pokemon like game. - Dariusz J. Mirończuk
        '''
    
    #CONSTRUCTOR
    def __init__(s):

        #INITALIZING PYGAME
        pygame.init()

        #LOADING IN LAUNCHER DATA
        s.loading_in_game_data()

        #SETTING UP THE DISPLAY
        s.setting_up_display()

        #INITALIZING DISPLAY
        s.display = pygame.display.set_mode((s.window_data['width'], s.window_data['height']), s.flags)
        s.window = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('[MONSTER MASTERS]')

        #INITALIZING CLOCK
        s.clock = pygame.time.Clock()
        s.fps = s.window_data['fps']

        #THREAD FOR LOADING ASSETS
        s.assets_loaded = False
        s.assets_thread = threading.Thread(target = s.import_assets, daemon = True)
        s.assets_thread.start()

        #CREATING STATE MANAGER AND STATES
        s.state_manager = StateManager(s)
        s.audio_manager = AudioManager(s)
        s.creating_states()


    #METHOD FOR IMPORTING ALL ASSETS
    def import_assets(s):
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers = 4) as executor:
            futures = [
                executor.submit(load_maps, s),
                executor.submit(load_assets, s),
                executor.submit(load_audio_assets, s),
                executor.submit(load_game_fonts, s)
            ]

            for f in futures:
                f.result()

        s.assets_loaded = True
        print('Assets loaded')

    #METHOD FOR LOADING IN LAUNCHER DATA
    def loading_in_game_data(s):
        s.window_data = load_data(WINDOW_DATA_PATH, DEFUALT_WINDOW_DATA)
        s.audio_data = load_data(AUDIO_DATA_PATH, DEFAULT_AUDIO_DATA)
        s.controlls_data = load_data(CONTROLLS_DATA_PATH, DEFAULT_CONTROLLS_DATA)

    #METHOD FOR CREATING STATE AND OS ELEMENTS (LIBRARY, STORE, SETTINGS, ...)
    def creating_states(s):
        s.state_manager.add_state('Singleplayer menu', SingleplayerMenu(s))
        s.state_manager.add_state('New save wizzard', NewSaveWizard(s))
        s.state_manager.add_state('Options menu', OptionsMenu(s))
        s.state_manager.add_state('Start menu', StartMenu(s))

        #SETTING CURRENT STATE
        s.state_manager.set_state('Start menu')

    #METHOD FOR SCALING MOUSE POSITTION
    def get_scaled_mouse_pos(s):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        scaled_x = mouse_x * (s.window.get_width() / s.display.get_width())
        scaled_y = mouse_y * (s.window.get_height() / s.display.get_height())

        return int(scaled_x), int(scaled_y)
    
    #METHOD FOR SETTING UP THE DISPLAY
    def setting_up_display(s):
        s.fullscreen = s.window_data['fullscreen']
        s.last_window_size = (s.window_data['width'], s.window_data['height'])

        if s.fullscreen:
            s.flags = pygame.FULLSCREEN
        else:
            s.flags = pygame.RESIZABLE
     
    #METHOD FOR SAVING THE LAUNCHER SETTINGS
    def save(s):
        save_data(s.window_data, WINDOW_DATA_PATH)
        save_data(s.audio_data, AUDIO_DATA_PATH)
        save_data(s.controlls_data, CONTROLLS_DATA_PATH)

        #SAVING THE GAME FILE
        current_state = s.state_manager.states[s.state_manager.current_state]
        if hasattr(current_state, "save"):
            current_state.save()

    #METHOD FOR HANDLING EVENTS
    def handling_events(s):
        events = pygame.event.get()


        for event in events:

            #CLOSING THE LAUNCHER IF WINDOW IS CLOSED
            if event.type == pygame.QUIT:
                s.save()
                pygame.quit()
                exit()

            #HANDLING WINDOW RESIZE
            if event.type == pygame.VIDEORESIZE and not s.fullscreen:

                #SAVING THE LAST NOT FULLSCREENED WINDOW SIZE
                s.window_data['width'] = event.w
                s.window_data['height'] = event.h

                #SETTING FULLSCREEN
                s.display = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                s.screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

                #SAVING CHANGES
                save_data(s.window_data, WINDOW_DATA_PATH)

            #USER BUTTON INPUT
            if event.type == pygame.KEYDOWN:

                #CLOSING LAUNCHER IF 'ESCAPE' BUTTON PRESSED
                if event.key == pygame.K_ESCAPE:
                    s.save()
                    pygame.quit()
                    exit()

                #TOGGLING FULLSCREEN MODE
                if event.key == pygame.K_9:
                    s.fullscreen = not s.fullscreen
                    s.window_data['fullscreen'] = s.fullscreen

                    if s.fullscreen:
                        s.last_window_size = (s.display.get_width(), s.display.get_height())
                        s.flags = pygame.FULLSCREEN
                        s.display = pygame.display.set_mode((s.window_data['width'], s.window_data['height']), s.flags)
                    else:
                        s.flags = pygame.RESIZABLE
                        s.display = pygame.display.set_mode(s.last_window_size, s.flags)
                        s.window_data['width'], s.window_data['height'] = s.last_window_size

                    save_data(s.window_data, WINDOW_DATA_PATH)

        #PASSING EVENTS TO THE CURRENT STATE
        s.state_manager.handling_events(events)

    #METHOD FOR UPDATING THE LAUNCHER
    def update(s):
        
        if s.fps is None:
            s.delta_time = s.clock.tick() / 1000
        else:
            s.delta_time = s.clock.tick(s.fps) / 1000


        # UPDATING CURRENT STATE
        s.state_manager.update(s.delta_time)

        #UPDATING AUDIO MANAGER
        s.audio_manager.update(s.delta_time)

    #METHOD FOR DRAWING THE LAUNCHER
    def draw(s):

        #FILLING THE WINDOW BLACK
        s.window.fill((255,0,0))

        #DRAWING THE CURRENT STATE
        s.state_manager.draw(s.window)

        #TRANSFORMING THE WINDOW TO PROPER DISPLAY | S.WINDOW ---> S.DISPLAY
        scaled_window = pygame.transform.scale(s.window, (s.display.get_width(), s.display.get_height()))

        #BLITTING THE SCALED WINDOW TO THE DISPLAY
        s.display.blit(scaled_window, (0,0))

        #UPDATING THE DISPLAY
        pygame.display.update()

    #METHOD FOR RUNNING THE LAUNCHER
    def run(s):

        #MAIN APPLICATION LOOP
        while True:

            #HANDILING EVENTS
            s.handling_events()

            #UPDATING THE GAME
            s.update()

            #DRAWING THE GAME
            s.draw()

#RUNNING THE LAUNCHER ONLY FROM THE MAIN FILE
if __name__ == '__main__':
    
    try:

        #RUNNING THE LAUNCHER
        game = Game()
        print(game)
        game.run()

    #CATCHING ANY ERRORS SO THE USER CAN TROUBLESHOOT
    except Exception as e:
        import traceback
        traceback.print_exc()
        input('Press [ENTER] to exit...')