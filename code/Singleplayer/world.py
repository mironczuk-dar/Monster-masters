#IMPORTING LIBRAIES
import pygame

#IMPORTING FILES
from Singleplayer.singleplayer_settings import *
from Singleplayer.camera import Camera
from Singleplayer.Support.overworld_support_functions import check_connection

#IMPORTING ENTITIES
from Singleplayer.player import Player
from Singleplayer.non_player_characters import NonPlayerCharacter

#IMPORTING SPRITES
from Singleplayer.overworld_sprites import Sprite, MapWall, TreeSprite, SmallTreeSprite, HouseSprite, GrassPatchSprite, AnimatedSprite, PortalSprite
from Singleplayer.dialog_tree import DialogTree

#IMPORTING DATA
from Manifest.npc_manifest import *

#WORLD CLASS
class World:

    #WORLD CONSTRUCTOR
    def __init__(s, game, singleplayer_state):

        #PASSING IN THE GAME
        s.game = game
        s.singleplayer_state = singleplayer_state

        #PLAYER POSITING AFTER LEAVING/ENTERING A BUILDING
        s.player_start_position = None
        s.portal_destination = None

        #EVENTS HAPPEINGNG IN GAME
        s.active_dialog = None

    #METHOD FOR DRAWING THE WORLD
    def draw(s, window):
        window.fill("#44C6C1")
        s.all_sprite_groups['all'].draw(window, s.player)

    #METHOD FOR UPDATING THE WORLD
    def update(s, delta_time):
        
        #UPDATING ALL THE SPRITES
        s.all_sprite_groups['all'].update(delta_time)

        #CHECKING PLAYER COLLISONS WITH THE MAP
        s.player_collisions(delta_time, 'horizontal')
        s.player_collisions(delta_time, 'vertical')

        #CHECKING PORTAL TRANSITIONS
        s.portal_check()

    #METHOD FOR ALL THE INPUTS
    def handling_events(s, events):

        key = pygame.key.get_just_pressed()
        keys = pygame.key.get_pressed()
        controlls = s.game.controlls_data

        if s.active_dialog:
            s.active_dialog.handling_events(events)
            return

        if key[controlls['action_a']]:
            for character in s.all_sprite_groups['characters']:
                if check_connection(80, s.player, character):
                    s.player.freeze_unfreeze()
                    character.change_facing_direction(s.player.rect.center)
                    s.create_dialog(character)
                    character.can_rotate = False

        if key[controlls['options']]:
            s.singleplayer_state.monster_index_active = True
            s.player.direction = vector(0,0)

        s.player.handling_events(events)

    #METHOD FOR CREATING THE DIALOG
    def create_dialog(s, character):
        if not s.active_dialog:
            s.active_dialog = DialogTree(s.game, s, s.player, character, s.all_sprite_groups, s.game.overworld_fonts['dialog'])

    #METHOD FOR CHECKING PLAYER / WALL COLLISIONS
    def player_collisions(s, delta_time, axis):

        #PLAYER MOVEMENT IN ONE OF THE AXISES
        s.player.move(delta_time, axis)

        for sprite in s.all_sprite_groups['collision']:
            if not sprite.hitbox.colliderect(s.player.hitbox):
                continue
            #HORIZONTAL COLLISION CHECK
            if axis == 'horizontal':

                if s.player.direction.x > 0:   #MOVING TO THE RIGHT
                    s.player.hitbox.right = sprite.hitbox.left

                elif s.player.direction.x < 0: #MOVING TO THE LEFT
                    s.player.hitbox.left = sprite.hitbox.right

                s.player.rect.centerx = s.player.hitbox.centerx - s.player.hitbox_offset_x

            #VERTICAL COLLISION CHECK
            else:

                if s.player.direction.y > 0:   #MOVING DOWN
                    s.player.hitbox.bottom = sprite.hitbox.top

                elif s.player.direction.y < 0: #MOVING UP
                    s.player.hitbox.top = sprite.hitbox.bottom

                s.player.rect.centery = s.player.hitbox.centery - s.player.hitbox_offset_y


            #STOPING THE CHECK AFTER ONE OF THE COLLISION
            break

    #METHOD FOR CHECKING TRANSITION PORTAL COLLISION
    def portal_check(s):
        sprites = [sprite for sprite in s.all_sprite_groups['portals']
                if sprite.rect.colliderect(s.player.hitbox)]

        if sprites:
            portal = sprites[0]

            s.player.frozen = True
            current_map = s.singleplayer_state.save_data['world_data']['current_map']
            print(current_map)

            s.portal_destination = portal.target[0]      #MAP THAT WILL BE LOADED
            s.player_start_position = current_map        #MAP FROM WHICH THE PLAYER CAME FROM
            s.singleplayer_state.tint_mode = 'tint'

    #METHOD FOR SETTING UP THE WORLD
    def setup(s, map_name = None):

        if map_name: #MAKING MAP AFTER GOING THROUGH PORTAL
            current_map = s.game.maps[map_name]
            s.current_map_name = map_name
            s.singleplayer_state.save_data['world_data']['current_map'] = map_name

        else:  #GAME FILE SAVE
            map_data = s.singleplayer_state.save_data['world_data']
            current_map = s.game.maps[map_data['current_map']]
            s.current_map_name = map_data['current_map']


        map_width = current_map.width * TILE_SIZE
        map_height = current_map.height * TILE_SIZE

        s.all_sprite_groups = {
            'all': Camera(s.game, map_width, map_height, s.game.overworld_frames['shadow']),
            'collision': pygame.sprite.Group(),
            'characters': pygame.sprite.Group(),
            'portals': pygame.sprite.Group()
        }

        final_pos = None
        if s.player_start_position:

            if 'Player' in [layer.name for layer in current_map.layers]:
                for object in current_map.get_layer_by_name('Player'):
                    if object.name == s.player_start_position:
                        facing_direction = object.properties['direction']
                        final_pos = (object.x, object.y)
                        break

            s.player_start_position = None

        if not final_pos:
            map_data = s.singleplayer_state.save_data['world_data']
            facing_direction = map_data['position']['facing_direction']
            final_pos = (
                map_data['position']['x'],
                map_data['position']['y']
            )

        #CREATING THE PLAYER
        s.player = Player(
            s.game,
            s.all_sprite_groups['all'],
            final_pos,
            s.game.overworld_frames['characters']['player'],
            facing_direction
        )

        #CREATING THE TERRAIN
        if 'Terrain' in [layer.name for layer in current_map.layers]:
            for x, y, surface in current_map.get_layer_by_name('Terrain').tiles():
                Sprite(s.all_sprite_groups['all'], (x*TILE_SIZE, y*TILE_SIZE), surface, WORLD_LAYERS['terrain'])

        #CREATING THE TERRAIN TOP
        if 'Terrain top' in [layer.name for layer in current_map.layers]:
            for x, y, surface in current_map.get_layer_by_name('Terrain top').tiles():
                Sprite(s.all_sprite_groups['all'], (x*TILE_SIZE, y*TILE_SIZE), surface, WORLD_LAYERS['terrain'])

        #CREATING MAP WALLS
        if 'Walls' in [layer.name for layer in current_map.layers]:
            for object in current_map.get_layer_by_name('Walls'):
                MapWall(s.all_sprite_groups['collision'], (object.x, object.y), pygame.Surface((object.width, object.height)))
                #MapWall((s.all_sprite_groups['all'], s.all_sprite_groups['collision']), (object.x, object.y), pygame.Surface((object.width, object.height)))   IF YOU WANT TO SEE THE WALLS

        #CREATING TRANSITION PORTALS
        if 'Portals' in [layer.name for layer in current_map.layers]:
            for object in current_map.get_layer_by_name('Portals'):
                PortalSprite(s.all_sprite_groups['portals'], (object.x, object.y), (object.width, object.height), (object.name, object.properties['place']))

        #CREATING OBJECTS
        if 'Objects' in [layer.name for layer in current_map.layers]:
            for object in current_map.get_layer_by_name('Objects'):
                if object.name == 'top':
                    Sprite(s.all_sprite_groups['all'], (object.x, object.y), object.image, WORLD_LAYERS['top'])
                else:
                    Sprite((s.all_sprite_groups['all'], s.all_sprite_groups['collision']), (object.x, object.y), object.image, WORLD_LAYERS['main'])

        #CREATING THE TREES
        if 'Trees' in [layer.name for layer in current_map.layers]:
            for object in current_map.get_layer_by_name('Trees'):
                TreeSprite((s.all_sprite_groups['all'], s.all_sprite_groups['collision']), (object.x, object.y), object.image, WORLD_LAYERS['main'])

        #CREATING THE TREES
        if 'Trees_small' in [layer.name for layer in current_map.layers]:
            for object in current_map.get_layer_by_name('Trees_small'):
                SmallTreeSprite((s.all_sprite_groups['all'], s.all_sprite_groups['collision']), (object.x, object.y), object.image, WORLD_LAYERS['main'])

        #CREATING THE BUILDINGS
        if 'Buildings' in [layer.name for layer in current_map.layers]:
            for object in current_map.get_layer_by_name('Buildings'):
                HouseSprite((s.all_sprite_groups['all'], s.all_sprite_groups['collision']), (object.x, object.y), object.image, WORLD_LAYERS['main'])

        #CREATING THE WATER
        if 'Water' in [layer.name for layer in current_map.layers]:
            for object in current_map.get_layer_by_name('Water'):
                for x in range(int(object.x), int(object.x + object.width), TILE_SIZE):
                    for y in range(int(object.y), int(object.y + object.height), TILE_SIZE):
                        AnimatedSprite(s.all_sprite_groups['all'], (x, y), s.game.overworld_frames['water'], WORLD_LAYERS['water'])

        #CREATING THE COASTS
        if 'Coast' in [layer.name for layer in current_map.layers]:
            for object in current_map.get_layer_by_name('Coast'):
                terrain = object.properties['terrain']
                side = object.properties['side']
                AnimatedSprite(s.all_sprite_groups['all'], (object.x, object.y), s.game.overworld_frames['coast'][terrain][side], WORLD_LAYERS['terrain'])

        #CREATING THE CHARACTERS
        if 'Characters' in [layer.name for layer in current_map.layers]:
            for object in current_map.get_layer_by_name('Characters'):
                NonPlayerCharacter(s.game,
                                   s,
                                   (s.all_sprite_groups['all'], s.all_sprite_groups['collision'], s.all_sprite_groups['characters']),
                                   (object.x, object.y), 
                                   s.game.overworld_frames['characters'][object.properties['model']],
                                   object.properties['direction'],
                                   object.properties['range'],
                                   object.name,
                                   s.singleplayer_state.save_data['flags_data']['characters_defeated'],
                                   character_id = object.name)

        #CREATING GRASS PATCHES
        if 'Grass' in [layer.name for layer in current_map.layers]:
            for object in current_map.get_layer_by_name('Grass'):
                GrassPatchSprite(s.all_sprite_groups['all'], (object.x, object.y), object.image, object.properties['biome'], WORLD_LAYERS['main'])

        #UNTINTING THE TINT WINDOW
        s.singleplayer_state.tint_mode = 'untint'