#IMPORTING LIBRARIES
import pygame

#IMPORTING FILES
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

#POPUP CLASS
class PopUp(pygame.sprite.Sprite):

    #CONSTRUCTOR
    def __init__(s, game, width, height, duration=7, pos="bottom-right", slide_speed=10):

        #SPRITE INHERITANCE
        super().__init__()

        #PASSING IN GAME AS AN ATTRIBUTE
        s.game = game

        #TIMING ATTRIBUTES
        s.timer = 0
        s.duration = duration
        s.slide_speed = slide_speed
        s.slide_in_to = True

        #POPUP SIZE AND SURFACE
        s.width, s.height = width, height
        s.image = pygame.Surface((s.width, s.height), pygame.SRCALPHA)
        s.rect = s.image.get_rect()

        #DETERMENING START AND TARGET POSITION BASED ON POS
        s.pos = pos
        s._set_positions(pos)

    #METHOD FOR CONFIGURING START AND TARGET POSITIONS FROM POPUP ANIMATION
    def _set_positions(s, pos):
        margin_x = 20
        margin_y = 150

        if pos == "bottom-right":
            s.rect.bottomright = (WINDOW_WIDTH + s.width, WINDOW_HEIGHT - margin_y)
            s.target_x = WINDOW_WIDTH - s.width - margin_x
        elif pos == "bottom-left":
            s.rect.bottomleft = (-s.width, WINDOW_HEIGHT - margin_y)
            s.target_x = margin_x
        else:
            raise ValueError(f"Unsupported popup position: {pos}")

    #METHOD FOR UPDATING
    def update(s, delta_time):

        #ADDING TO POPUP TIMER
        s.timer += delta_time

        #SLIDING IN
        if s.slide_in_to:
            direction = -1 if s.pos.endswith("right") else 1
            s.rect.x += direction * s.slide_speed * delta_time * 60
            if (direction == -1 and s.rect.x <= s.target_x) or (direction == 1 and s.rect.x >= s.target_x):
                s.rect.x = s.target_x
        
        #SLIDING OUT
        else:
            direction = 1 if s.pos.endswith("right") else -1
            s.rect.x += direction * s.slide_speed * delta_time * 60

            #REMOVING POPUP IF FULLY OFF SCREEN
            if (direction == 1 and s.rect.left > WINDOW_WIDTH) or (direction == -1 and s.rect.right < 0):
                s.kill()

        #SWITCHING TO SLIDING OUT AFTER TIMER DURATION
        if s.timer >= s.duration:
            s.slide_in_to = False

    #METHOD FOR DRAWING
    def draw(s, surface):
        surface.blit(s.image, s.rect)

    #DUMMY DRAW ELEMENT METHOD FOR CHILD CLASSES
    def draw_elements(s):
        """To be implemented by child classes to fill `s.image`."""
        pass



#MUSIC POPUP CLASS
class MusicPopUp(PopUp):

    #CONSTRUCTOR
    def __init__(s, game, track_name, duration=5):

        #POPUP INHERITANCE
        super().__init__(game, width=300, height=80, duration=duration, pos="bottom-left")

        #POPUP DATA
        s.track_name = track_name

        #SURFACE ATTRIBUTES
        s.bg_color = (0, 0, 0, 200)
        s.font_title = pygame.font.SysFont(None, 28)
        s.text_surface = s.font_title.render(f"{track_name}", True, (255, 255, 255))

        #DRAWING ELEMENTS
        s.draw_elements()

    #METHOD FOR DRAWING ELEMENTS TO ONE SURFACE
    def draw_elements(s):
        s.image.fill(s.bg_color)
        s.image.blit(s.text_surface, (10, 25))
