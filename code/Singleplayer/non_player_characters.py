#IMPORTING LIBRARIES
import pygame
from random import choice, randint
from pygame.math import Vector2 as vector

#IMPORTING FILES
from Singleplayer.singleplayer_settings import WORLD_LAYERS, ANIMATION_SPEED
from Singleplayer.Support.overworld_support_functions import check_connection
from Tools.timer import Timer

#IMPORTING DATA
from Manifest.npc_manifest import CHARACTER_DATA

class NonPlayerCharacter(pygame.sprite.Sprite):
    def __init__(s, game, world, groups, pos, frames, facing_direction, range, character_name, defeated_characters):
        super().__init__(groups)

        #PASSING IN GAME AS AN ATTRIBUTE
        s.game = game
        s.world = world
        s.level_depth = WORLD_LAYERS['main']
        s.player = s.world.player
        s.create_dialog = s.world.create_dialog
        s.collision_rects = [sprite.rect for sprite in s.world.all_sprite_groups['collision'] if sprite is not s]
        
        #THE CHARACTERS DATA
        s.character_name = character_name
        s.character_data = CHARACTER_DATA[character_name]
        s.defeated = True if s.character_name in defeated_characters else False

        #ANIMATION ATTRIBUTES
        s.frames = frames
        s.frame_index = 0
        s.facing_direction = facing_direction

        #PLAYER MOVEMENT
        s.has_moved = False
        s.can_rotate = True
        s.has_noticed = False
        s.range = range
        s.view_directions = s.character_data['directions']
        s.movement_speed = 300
        s.direction = vector()

        #SPRITE ATTRIBUTES
        s.image = s.frames[s.get_state()][s.frame_index]
        s.rect = s.image.get_frect(center = pos)
        s.hitbox = s.rect.inflate(-s.rect.width/2, -80)

        #HITBOX OFFSET
        s.hitbox_offset_x = 0
        s.hitbox_offset_y = 37
        s.hitbox.center = (s.rect.centerx + s.hitbox_offset_x,
                   s.rect.centery + s.hitbox_offset_y)
        
        #CHARACTER TIMERS
        s.timers = {
            'look around' : Timer(randint(500, 1500), autostart = True, repeat= True, function = s.change_looking_direction),
            'notice' : Timer(500, function = s.start_move)
        }

    #METHOD FOR CHANGING CHARACTER LOOKING DIRECTION
    def change_looking_direction(s):
        if s.can_rotate:
            s.facing_direction = choice(s.view_directions)
        
    #METHOD FOR STARTING NPC MOVEMENT
    def start_move(s):
        relation = (vector(s.player.rect.center) - vector(s.rect.center)).normalize()
        s.direction = vector(round(relation.x), round(relation.y))
        
    #METHOD FOR CASTING RAY TO WHICH THE NPC CAN WALK UP TO THE PLAYER
    def ray_cast(s):
        if check_connection(s.range, s, s.player) and s.has_line_of_sight() and not s.has_noticed:
            s.has_noticed = True
            s.can_rotate = False
            s.player.noticed = True
            s.player.freeze_unfreeze()
            s.player.change_facing_direction(s.rect.center)
            s.timers['notice'].activate()

    #METHOD FOR CHECKING THE NPC LINE OF SIGHT
    def has_line_of_sight(s):
        if vector(s.rect.center).distance_to(s.player.rect.center) < s.range:

            line_blocked = any(rect.clipline(s.rect.center, s.player.rect.center) 
                            for rect in s.collision_rects)
            
            return not line_blocked
    
        return False
        
    #METHOD FOR GETTING DIALOG
    def get_dialog(s):
        if not s.defeated:
            return s.character_data['dialog']['default']
        else:
            return s.character_data['dialog']['defeated']
        
    #METHOD FOR CHANING THE CHARACTERS DIRECTION
    def change_facing_direction(s, target_pos):
        relation = vector(target_pos) - vector(s.rect.center)
        if abs(relation.y) < 30:
            s.facing_direction = 'right' if relation.x > 0 else 'left'
        else:
            s.facing_direction = 'down' if relation.y > 0 else 'up'

    #METHOD FOR MOVING THE PLAYER
    def move(s, delta_time):

        if not s.has_moved and s.direction:
            if not s.hitbox.inflate(10,10).colliderect(s.player.hitbox):
                s.rect.centerx += s.direction.x * s.movement_speed * delta_time
                s.hitbox.centerx = s.rect.centerx + s.hitbox_offset_x
                s.rect.centery += s.direction.y * s.movement_speed * delta_time
                s.hitbox.centery = s.rect.centery + s.hitbox_offset_y
            else:
                s.direction = vector(0,0)
                s.has_moved = True
                s.player.noticed = False
                s.create_dialog(s)

    #METHOD FOR UPDATING THE PLAYER
    def update(s, delta_time):
        s.animate(delta_time)

        if s.character_data['look_around']:
            s.move(delta_time)
            s.ray_cast()

        for timer in s.timers.values():
            timer.update()

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