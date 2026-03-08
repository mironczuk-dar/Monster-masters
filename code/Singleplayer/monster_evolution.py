#IMPORTING LIBRARIES
import pygame

#IMPORTING TOOLS
from Tools.timer import Timer


class EvolutionEffect(pygame.sprite.Sprite):
    def __init__(s, game, frames, start_monster, end_monster, font, end_evolution):

        super().__init__()
        
        #PASSING IN GAME AS AN ATTRIBUTE
        s.game = game

        #ANIMATION ATTRIBUTES
        s.start_monster_surface = pygame.transform.scale2x(frames[start_monster]['idle'][0])
        s.end_monster_surface = pygame.transform.scale2x(frames[end_monster]['idle'][0])

        #TIMERS
        s.timer = {
            'start' : Timer(800, autostart = True),
            'end' : Timer(1800, function = end_evolution)
        }

    def update(s, delta_time):
        for timer in s.timer.values():
            timer.update()

        if not s.timer['start'].active:
            pass

    def draw(s, window):
        window.blit(s.image, s.rect)

        #SETTING UP THE SPRITE
        s.image = s.frames[s.frame_index]
        s.rect = s.image.get_frect(center=(s.game.window.get_width() // 2, s.game.window.get_height() // 2))

        s.animation_timer = Timer(s.animation_speed, repeat=True, function=s.update_animation)
        