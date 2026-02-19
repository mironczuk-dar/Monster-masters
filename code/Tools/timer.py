#IMPORTING LIBRARIES
import pygame

#INVERSAL TIMER TOOL
class Timer:
    
    #TIMER CLASS CONSTRUCTOR
    def __init__(s, duration, autostart = False, function = None, repeat = False):
        s.duration = duration
        s.function = function
        s.start_time = 0
        s.active = False
        s.repeat = repeat
        s.autostart = autostart

        if s.autostart:
            s.activate()

    #METHOD FOR ACTIVATING THE TIMER
    def activate(s):
        s.active = True
        s.start_time = pygame.time.get_ticks()

    #METHOD FOR DEACTIVATING THE TIMER
    def deactivate(s):
        s.active = False
        s.start_time = 0
        
        if s.repeat:
            s.activate()

    #METHOD FOR UPDATING THE TIMER
    def update(s):
        if not s.active:
            return
        
        current_time = pygame.time.get_ticks()

        if current_time - s.start_time >= s.duration:
            if s.function and s.start_time != 0:
                s.function()
            s.deactivate()