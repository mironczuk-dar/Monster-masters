#IMPORTING LIBRARIES
import pygame
from random import uniform

#IMPORTING FILES
from Singleplayer.singleplayer_settings import *
from Tools.timer import Timer

#IMPORTING UI ELEMENTS
from UI_elements.bar import draw_bar

class TimedSprite(pygame.sprite.Sprite):
    def __init__(s, groups, pos, surface, duration):
        super().__init__(groups)

        s.image = surface
        s.rect = s.image.get_frect(center = pos)
        s.z = BATTLE_LAYERS['overlay']
        s.death_timer = Timer(duration, True, s.kill)

    def update(s, update):
        s.death_timer.update()
        

class AttackSprite(pygame.sprite.Sprite):
    def __init__(s, groups, pos, frames, level_depth = BATTLE_LAYERS['overlay']):

        super().__init__(groups)

        s.frames = frames
        s.frame_index = 0
        s.z = level_depth

        s.image = s.frames[s.frame_index]
        s.rect = s.image.get_frect(topleft = pos)
        s.level_depth = level_depth
        s.hitbox = s.rect.copy()
        s.rect.center = pos

    def update(s, delta_time):
        s.animate(delta_time)

    def animate(s, delta_time):
        s.frame_index += ANIMATION_SPEED * delta_time
        if s.frame_index < len(s.frames):
            s.image = s.frames[int(s.frame_index)]
        else:
            s.kill()

class MonsterSprite(pygame.sprite.Sprite):
    def __init__(s, groups, pos, frames, monster, index, entity, apply_attack, create_monster):
        super().__init__(groups)

        #MONSTER SPRITE ATTRIBUETS
        s.index = index
        s.pos = pos
        s.entity = entity
        s.monster = monster
        s.z = BATTLE_LAYERS['monster']

        #HIGHLIGHT ATTRIBUTES
        s.highlight = False

        #ATTACKING ATTRIBUTES
        s.target_sprite = None
        s.current_attack = None
        s.apply_attack = apply_attack
        s.create_monster = create_monster

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
            'remove_highlight' : Timer(100, False, function= lambda: s.set_highlight(False)),
            'kill' : Timer(600, False, s.destroy)
        }

    def activate_attack(s, target_sprite, attack):
        s.state = 'attack'
        s.frame_index = 0
        s.target_sprite = target_sprite
        s.current_attack = attack
        s.monster.reduce_energy(attack)

    def delayed_kill(s, new_monster):
        if not s.timers['kill'].active:
            s.next_monster_data = new_monster
            s.timers['kill'].activate()

    def destroy(s):
        if s.next_monster_data and s.next_monster_data[0] is not None:
            monster, index, entity = s.next_monster_data
            s.create_monster(monster, index, entity, s.pos)
        s.kill()

    def animate(s, delta_time):
        s.frame_index += s.animation_speed * delta_time
        
        if s.state == 'attack' and s.frame_index >= len(s.frames['attack']):
            s.state = 'idle'
            s.frame_index = 0
            s.apply_attack(s.target_sprite, s.current_attack, s.monster.get_base_damage(s.current_attack))
        
        current_frames = s.frames[s.state]
        s.adjusted_frame_index = int(s.frame_index % len(current_frames))
        s.image = current_frames[s.adjusted_frame_index]

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

        if not s.monster_sprite.groups():
            s.kill()

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

    def update(s, delta_time):
        if not s.monster_sprite.groups():
            s.kill()

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

        if not s.monster_sprite.groups():
            s.kill()

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

        if not s.monster_sprite.groups():
            s.kill()