#IMPORTING LIBRARIES
import pygame


#A GENERIC BUTTON CLASS
class GenericButton():
    def __init__(s, game, size, pos, text, text_size=40, text_colour=(0,0,0), colour=(255, 0, 0), action=None):

        #PASSING IN THE GAME AS AN ATTIBUTE
        s.game = game
        s.action = action

        #CREATING BUTTON SURFACE
        s.image = pygame.Surface(size, pygame.SRCALPHA)
        s.image.fill(colour)
        s.rect = s.image.get_rect(center=pos)

        #RENDERING BUTTON TEXT
        s.font = pygame.font.Font(None, text_size)
        text_surf = s.font.render(text, True, text_colour)
        
        #SETTING CENTER OF TEXT
        text_rect = text_surf.get_rect(center=(size[0] // 2, size[1] // 2))
        
        #ADDING TEXT TO THE BUTTON IMAGE
        s.image.blit(text_surf, text_rect)

    def update(s, delta_time):
        pass

    def draw(s, window):
        window.blit(s.image, s.rect)

    def handling_events(s, events):
        mouse_pos = s.game.get_scaled_mouse_pos()
        mouse_press = pygame.mouse.get_just_pressed()[0]

        if s.rect.collidepoint(mouse_pos):
            s.image.set_alpha(100)
        else:
            s.image.set_alpha(255)

        if s.rect.collidepoint(mouse_pos) and mouse_press:
            if s.action:
                s.action()


#A TOGGLE BUTTON
class ToggleButton:
    def __init__(s, game, size, pos, text, text_size=40, active_colour=(0, 255, 0), inactive_colour=(255, 0, 0), action=None):
        
        #PASSING IN GAME AS AN ATTRIBUTE
        s.game = game

        #TOGGLE BUTTON ATTRIBUTES
        s.size = size
        s.pos = pos
        s.text = text
        s.text_size = text_size
        s.action = action

        #COLOURS FOR BOTH STATES
        s.active_colour = active_colour
        s.inactive_colour = inactive_colour
        
        #BUTTON STATE
        s.is_on = False
        
        #BUTTON FONT
        s.font = pygame.font.Font(None, s.text_size)

        #SETTING THE FIST APPERANCE
        s.update_appearance()

    #METHOD FOR SETTING UP/CHANGING THE APPERACE
    def update_appearance(s):
        s.image = pygame.Surface(s.size, pygame.SRCALPHA)
        current_colour = s.active_colour if s.is_on else s.inactive_colour
        s.image.fill(current_colour)
        
        s.rect = s.image.get_rect(center=s.pos)
        
        #RENDERING THE TEXT
        text_surf = s.font.render(s.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(s.size[0] // 2, s.size[1] // 2))
        s.image.blit(text_surf, text_rect)

    #METHOD FOR DRAWING THE TOGGLE BUTTON
    def draw(s, window):
        window.blit(s.image, s.rect)

    #METHOD FOR UPDATING THE TOGGLE BUTTON
    def update(s, delta_time):
        """Empty to skip AttributeError."""
        pass

    #METHOD FOR HANDLING THE EVENTS
    def handling_events(s, events):
        mouse_pos = s.game.get_scaled_mouse_pos()
        
        #HOVERING EFECT
        if s.rect.collidepoint(mouse_pos):
            s.image.set_alpha(180)
        else:
            s.image.set_alpha(255)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Lewy przycisk myszy
                    if s.rect.collidepoint(mouse_pos):
                        s.toggle()

    #METHOD FOR TOGGLING THE BUTTON
    def toggle(s):
        s.is_on = not s.is_on
        s.update_appearance() # Zmieniamy kolor
        if s.action:
            s.action() # Wywołujemy funkcję (np. toggle_remove_mode)