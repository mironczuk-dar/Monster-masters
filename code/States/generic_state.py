#IMPORTING LIBRARIES
import pygame

#A GENERIC STATE CLASS FOR CREATING NEW STATES
class BaseState:
    def __init__(s, game):
        s.game = game

    #HANDLING INPUTS/EVENTS
    def handling_events(s, events):
        """
        Obsługa inputu lokalnego stanu.
        Globalny input (TAB, sidebar) jest w StateManager.
        """
        pass

    #METHOD FOR UPDATING THE CLASS
    def update(s, delta_time):
        """
        Logika stanu.
        Sidebar i focus NIE są tu aktualizowane.
        """
        pass

    #METHOD FOR DRAWING THE CLASS
    def draw(s, window):
        """
        Rysowanie zawartości stanu.
        Sidebar rysowany jest w StateManager.
        """
        pass

    #REFRESHING THE CLASS ELEMETS ON ENTER
    def on_enter(s):
        pass
