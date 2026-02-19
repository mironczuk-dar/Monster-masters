# IMPORTING FILES
from settings import *
from pygame.math import Vector2 as vector
import pygame
from Singleplayer.non_player_characters import NonPlayerCharacter
from Singleplayer.player import Player


# CAMERA CLASS
class Camera(pygame.sprite.Group):

    def __init__(s, game, map_width, map_height, shadow):
        super().__init__()

        s.offset = vector()
        s.map_width = map_width
        s.map_height = map_height

        s.visual_processed_sprites = 0
        s.update_processed_sprites = 0

        s.depth_tilt = 0.82
        s.shadow = shadow

        s.notice_surface = game.overworld_frames['notice_mark']

    def _depth_sort_key(s, sprite):

        layer = getattr(sprite, "level_depth", 0)

        # custom depth anchor
        if hasattr(sprite, "depth_anchor"):
            y = sprite.depth_anchor()
        else:
            y = sprite.rect.top + sprite.rect.height * s.depth_tilt

        return (layer, y)

    def draw(s, surface, target):

        # CAMERA OFFSET
        target_offset_x = target.rect.centerx - WINDOW_WIDTH / 2
        target_offset_y = target.rect.centery - WINDOW_HEIGHT / 2

        if s.map_width > WINDOW_WIDTH:
            s.offset.x += (target_offset_x - s.offset.x) * 0.1
            s.offset.x = max(0, min(s.offset.x,
                                    s.map_width - WINDOW_WIDTH))
        else:
            s.offset.x = (s.map_width - WINDOW_WIDTH) / 2

        if s.map_height > WINDOW_HEIGHT:
            s.offset.y += (target_offset_y - s.offset.y) * 0.1
            s.offset.y = max(0, min(s.offset.y,
                                    s.map_height - WINDOW_HEIGHT))
        else:
            s.offset.y = (s.map_height - WINDOW_HEIGHT) / 2


        # SCREEN CULLING
        visual_screen_rect = pygame.Rect(
            s.offset.x,
            s.offset.y,
            WINDOW_WIDTH * 1.1,
            WINDOW_HEIGHT * 1.1
        )
        s.visual_processed_sprites = 0

        for sprite in sorted(s.sprites(), key=s._depth_sort_key):
            if visual_screen_rect.colliderect(sprite.rect):
                s.visual_processed_sprites += 1

                #DRAWING THE SHADOW UNDER THE PLAYER AND NPC'S
                if isinstance(sprite, (NonPlayerCharacter, Player)):
                    shadow_rect = s.shadow.get_rect(midbottom = sprite.rect.midbottom)
                    surface.blit(s.shadow, shadow_rect.topleft - s.offset)

                #DRAWING THE ACTUAL SPRITES
                if hasattr(sprite, "draw"):
                    sprite.draw(surface, s.offset)
                else:
                    surface.blit(sprite.image, sprite.rect.topleft - s.offset)

                #DRAWING THE NOTICE MARK
                if sprite == target and target.noticed:
                    rect = s.notice_surface.get_frect(midbottom = sprite.rect.midtop)
                    surface.blit(s.notice_surface, rect.topleft - s.offset)


    def update(s, delta_time):

        update_screen_rect = pygame.Rect(
            s.offset.x,
            s.offset.y,
            WINDOW_WIDTH * 1.5,
            WINDOW_HEIGHT * 1.5
        )

        s.update_processed_sprites = 0

        for sprite in s.sprites():

            if update_screen_rect.colliderect(sprite.rect):

                s.update_processed_sprites += 1

                if hasattr(sprite, "update"):
                    sprite.update(delta_time)