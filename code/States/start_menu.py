# IMPORTING LIBRARIES
import pygame
import sys

# IMPORTING FILES
from States.generic_state import BaseState
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from UI_elements.buttons import GenericButton

#STARTER MENU CLASS
class StartMenu(BaseState):
    def __init__(s, game):
        super().__init__(game)

        #MAIN MENU BACKGROUND
        s.background = pygame.Surface((s.game.window.get_width(), s.game.window.get_height()))
        s.background.fill('#ADD8E6')

        #GAME VERSION TEXT
        s.font = pygame.font.SysFont(None, 40)
        s.game_version = s.font.render(
            'Version: ALPHA 1.0.0',
            False,
            (0, 0, 0)
        )

        #BUTTONS
        s.buttons = []

        #STATES FROM STATE MANAGER
        s.start_menu_elements = s.game.state_manager.states

        #SETUP STARTING MENU
        s.setup()

    #METHOD FOR UPDATING THE MENU
    def update(s, delta_time):

        for button in s.buttons:
            button.update(delta_time)

    #METHOD FOR HANDLING THE EVENTS
    def handling_events(s, events):
        for button in s.buttons:
            button.handling_events(events)

    #METHOD FOR DRAWING THE CLASS
    def draw(s, window):

        window.blit(s.background, (0, 0))

        window.blit(
            s.game_version,
            (
                WINDOW_WIDTH - s.game_version.get_width() - 10,
                WINDOW_HEIGHT - s.game_version.get_height() - 2
            )
        )

        for button in s.buttons:
            button.draw(window)

    #EXIT ACTION
    def exit_game(s):
        s.game.save()
        pygame.quit()
        sys.exit()

    #METHOD FOR SETTING UP THE MENU
    def setup(s):
        size = (250, 80)
        pos_x = 130 
        pos_y = 80

        # Lista stanów, które mają być widoczne w menu
        visible_states = ["Singleplayer menu", "Options menu"]

        for key in visible_states:
            btn = GenericButton(
                s.game,
                size,
                (pos_x, pos_y),
                key,
                action=lambda k=key: s.game.state_manager.change_state(k)
            )
            s.buttons.append(btn)
            pos_y += size[1] + 10

        # Dodanie przycisku Exit
        exit_btn = GenericButton(
            s.game,
            size,
            (pos_x, pos_y),
            "Exit Game",
            action=s.exit_game
        )
        s.buttons.append(exit_btn)

