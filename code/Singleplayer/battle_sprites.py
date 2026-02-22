#IMPORTING LIBRARIES
import pygame
from random import uniform

#IMPORTING FILES
from Singleplayer.singleplayer_settings import *
from Tools.timer import Timer

#IMPORTING UI ELEMENTS
from UI_elements.bar import draw_bar

class MonsterSprite(pygame.sprite.Sprite):
    def __init__(s, groups, pos, frames, monster, index, entity):
        super().__init__(groups)

        #MONSTER SPRITE ATTRIBUETS
        s.index = index
        s.pos = pos
        s.entity = entity
        s.monster = monster
        s.z = BATTLE_LAYERS['monster']

        #HIGHLIGHT ATTRIBUTES
        s.highlight = False

        #ANIMATION ATTRIBUTES
        s.frame_index = 0
        s.frames = frames
        s.state = 'idle'
        s.animation_speed = ANIMATION_SPEED + uniform(-1, 1)

        #SPRITE SETUP
        s.image = s.frames[s.state][s.frame_index]
        s.rect = s.image.get_frect(center = s.pos)

        #TIMERS
        s.timers = {
            'remove_highlight' : Timer(100, False, function= lambda: s.set_highlight(False))
        }


    def animate(s, delta_time):
        s.frame_index += s.animation_speed * delta_time
        s.adjusted_frame_index = int(s.frame_index % len(s.frames[s.state]))
        s.image = s.frames[s.state][s.adjusted_frame_index]

        if s.highlight:
            white_surface = pygame.mask.from_surface(s.image).to_surface()
            white_surface.set_colorkey('black')
            s.image = white_surface

    def update(s, delta_time):
        s.animate(delta_time)
        s.monster.update(delta_time)
        for timer in s.timers.values():
            timer.update()

    def set_highlight(s, value):
        s.highlight = value
        if value: 
            s.timers['remove_highlight'].activate()

class MonsterOutlineSprite(pygame.sprite.Sprite):
    def __init__(s, monster_sprite, groups, frames):
        super().__init__(groups)

        s.z = BATTLE_LAYERS['outline']
        s.monster_sprite = monster_sprite
        s.frames = frames

        s.image = s.frames[s.monster_sprite.state][s.monster_sprite.frame_index]
        s.rect = s.image.get_frect(center = s.monster_sprite.rect.center)

    def update(s, delta_time):
        s.image = s.frames[s.monster_sprite.state][s.monster_sprite.adjusted_frame_index]
        s.rect.center = s.monster_sprite.rect.center

class MonsterNameSprite(pygame.sprite.Sprite):
    def __init__(s, groups, pos, monster_sprite, font):

        super().__init__(groups)
        s.monster_sprite = monster_sprite
        s.z = BATTLE_LAYERS['name']

        text_surface = font.render(monster_sprite.monster.name, False, COLORS['black'])
        padding = 10

        s.image = pygame.Surface((text_surface.get_width() + padding*2, text_surface.get_height() + padding*2))
        s.image.fill(COLORS['white'])
        s.image.blit(text_surface, (padding, padding))
        s.rect = s.image.get_frect(midtop = pos)

class MonsterLevelSprite(pygame.sprite.Sprite):
    def __init__(s, groups, entity, pos, monster_sprite, font):

        super().__init__(groups)
        s.monster_sprite = monster_sprite
        s.font = font
        s.z = BATTLE_LAYERS['name']


        s.image = pygame.Surface((90,40))
        s.rect = s.image.get_frect(topleft = pos) if entity == 'player' else s.image.get_frect(topright = pos)
        s.exp_rect = pygame.FRect(0, s.rect.height - 4, s.rect.width, 6)

    def update(s, delta_time):
        s.image.fill(COLORS['white'])
        text_surface = s.font.render(f'Lvl: {s.monster_sprite.monster.level}', False, COLORS['black'])
        text_rect = text_surface.get_frect(center = (s.rect.width/2, s.rect.height/2))
        s.image.blit(text_surface, text_rect)

        draw_bar(s.image, s.exp_rect, s.monster_sprite.monster.exp, s.monster_sprite.monster.level_up, COLORS['blue'], COLORS['black'], 0)

class MonsterStatsSprite(pygame.sprite.Sprite):
    def __init__(s, groups, pos, monster_sprite, size, font):
        super().__init__(groups)
        s.monster_sprite = monster_sprite
        s.image = pygame.Surface(size)
        s.rect = s.image.get_frect(midbottom = pos)
        s.font = font
        s.z = BATTLE_LAYERS['overlay']

    def update(s, delta_time):
        s.image.fill(COLORS['white'])
        
        for index, (value, max_value) in enumerate(s.monster_sprite.monster.get_info()):
            colour = (COLORS['red'], COLORS['blue'], COLORS['grey'])[index]

            if index < 2:
                text_str = f'{int(value)}/{int(max_value)}'
                text_surface = s.font.render(text_str, False, COLORS['black'])
                
                text_rect = text_surface.get_frect(topleft = (s.image.get_width() * 0.05, index * s.image.get_height() / 2.2))
                s.image.blit(text_surface, text_rect)

                bar_rect = pygame.FRect(text_rect.bottomleft + pygame.Vector2(0, 2), (s.image.get_width() * 0.9, 6))
                draw_bar(s.image, bar_rect, value, max_value, colour, COLORS['black'], 2)

            else:
                bar_height = 6
                init_rect = pygame.FRect((0, s.image.get_height() - bar_height), (s.image.get_width(), bar_height))
                draw_bar(s.image, init_rect, value, max_value, colour, COLORS['white'], 0)