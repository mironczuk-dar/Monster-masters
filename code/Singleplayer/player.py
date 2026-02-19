#IMPORTING LIBRARIES
import pygame
from pygame.math import Vector2 as vector

#IMPORTING FILES
from Singleplayer.singleplayer_settings import WORLD_LAYERS, ANIMATION_SPEED


class Player(pygame.sprite.Sprite):
    def __init__(s, game, groups, pos, frames, facing_direction):
        super().__init__(groups)

        #PASSING IN GAME AS AN ATTRIBUTE
        s.game = game
        s.level_depth = WORLD_LAYERS['main']

        #ANIMATION ATTRIBUTES
        s.frames = frames
        s.frame_index = 0
        s.facing_direction = facing_direction

        #PLAYER MOVEMENT
        s.movement_speed = 300
        s.direction = vector()
        s.frozen = False

        #SPRITE ATTRIBUTES
        s.image = s.frames[s.get_state()][s.frame_index]
        s.rect = s.image.get_frect(center = pos)
        s.hitbox = s.rect.inflate(-s.rect.width/2-30, -80)

        #HITBOX OFFSET
        s.hitbox_offset_x = 0
        s.hitbox_offset_y = 37
        s.hitbox.center = (s.rect.centerx + s.hitbox_offset_x,
                   s.rect.centery + s.hitbox_offset_y)
        
        #DIALOG FLAGS
        s.noticed = False

    #METHOD FOR FREEZING THE PLAYER SO HE DOESN'T MOVE
    def freeze_unfreeze(s):
        s.direction = vector(0,0)
        s.frozen = not s.frozen

    #METHOD FOR CHANING THE PLAYERS DIRECTION
    def change_facing_direction(s, target_pos):
        relation = vector(target_pos) - vector(s.rect.center)
        if abs(relation.y) < 30:
            s.facing_direction = 'right' if relation.x > 0 else 'left'
        else:
            s.facing_direction = 'down' if relation.y > 0 else 'up'

    #METHOD FOR HANDLING PLAYER INPUT
    def handling_events(s, events):
        controlls = s.game.controlls_data
        
        #GETTING PLAYER INPUT
        keys = pygame.key.get_pressed()
        input_vector = vector()

        if not s.frozen:

            if keys[controlls['up']]:
                input_vector.y -= 1
            elif keys[controlls['down']]:
                input_vector.y += 1
            
            if keys[controlls['left']]:
                input_vector.x -= 1
            if keys[controlls['right']]:
                input_vector.x += 1

            if input_vector.length() > 0:
                input_vector = input_vector.normalize()

            s.direction = input_vector

    #METHOD FOR MOVING THE PLAYER
    def move(s, delta_time, axis):

        if not s.frozen:

            if axis == 'horizontal':
                s.rect.centerx += s.direction.x * s.movement_speed * delta_time
                s.hitbox.centerx = s.rect.centerx + s.hitbox_offset_x
            else:
                s.rect.centery += s.direction.y * s.movement_speed * delta_time
                s.hitbox.centery = s.rect.centery + s.hitbox_offset_y

    #METHOD FOR UPDATING THE PLAYER
    def update(s, delta_time):
        s.animate(delta_time)

    #METHOD FOR ANIMATION
    def animate(s, delta_time):
        s.frame_index += ANIMATION_SPEED * delta_time
        s.image = s.frames[s.get_state()][int(s.frame_index % len(s.frames[s.get_state()]))]

    #METHOD FOR GETTING STATE FOR ANIMATION
    def get_state(s):
        moving = bool(s.direction)
        if moving:
            if s.direction.x != 0:
                s.facing_direction = 'right' if s.direction.x > 0 else 'left'
            if s.direction.y != 0:
                s.facing_direction = 'down' if s.direction.y > 0 else 'up'
        return f'{s.facing_direction}{"" if moving else "_idle"}'
    
    def depth_anchor(self):
        return self.rect.bottom


