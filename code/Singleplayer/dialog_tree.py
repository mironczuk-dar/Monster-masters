#IMPORTING LIBRARIES
import pygame

#IMPORTING FILES
from Singleplayer.singleplayer_settings import *

#IMPORTING DATA
from Manifest.npc_manifest import *


class DialogTree:
    def __init__(s, game, world, player, character, all_sprite_groups, font):

        #DIALOG TREE ATTRIBUTES
        s.game = game
        s.world = world
        s.player = player
        s.character = character
        s.sprite_groups = all_sprite_groups
        s.font = font

        s.dialog = character.get_dialog()
        s.dialog_number = len(s.dialog)
        s.dialog_index = 0

        s.current_dialog = DialogSprite(s.sprite_groups['all'], s.character, s.dialog[s.dialog_index], s.font)

    def handling_events(s, events):
        controlls = s.game.controlls_data
        key = pygame.key.get_just_pressed()

        if key[controlls['action_a']] or key[controlls['action_b']]:

            s.current_dialog.kill()
            s.dialog_index += 1

            if s.dialog_index < s.dialog_number:
                s.current_dialog = DialogSprite(s.sprite_groups['all'], s.character, s.dialog[s.dialog_index], s.font)
            
            else:
                s.end_dialog()

    def end_dialog(s):
        s.player.freeze_unfreeze()
        s.world.active_dialog = None

class DialogSprite(pygame.sprite.Sprite):
    def __init__(s, groups, character, message, font):
        super().__init__(groups)

        s.level_depth = WORLD_LAYERS['top']

        #TEXT
        text_surface = font.render(message, False, COLORS['black'])
        padding = 15
        width = max(30, text_surface.get_width() + padding * 2)
        height = text_surface.get_height() + padding * 2

        #BACKGROUND SURFACE
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((0,0,0,0))
        pygame.draw.rect(surface, COLORS['pure white'], surface.get_frect(topleft = (0,0)), 0, 20)
        surface.blit(text_surface, text_surface.get_frect(center = (width/2, height/2)))

        s.image = surface
        s.rect = s.image.get_frect(midbottom = character.rect.midtop + vector(0, -10))