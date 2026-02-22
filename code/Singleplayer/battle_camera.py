#IMPORTING LIBRARIES
import pygame

#IMPORTING FILES
from Singleplayer.singleplayer_settings import BATTLE_LAYERS

class BattleSprites(pygame.sprite.Group):
    def __init__(s, game):
        super().__init__()

        s.game = game

    def draw(s, window, current_monster_sprite):

        for sprite in sorted(s, key = lambda sprite: sprite.z):
            if sprite.z == BATTLE_LAYERS['outline']:
                if sprite.monster_sprite == current_monster_sprite:
                    window.blit(sprite.image, sprite.rect)
            else:
                window.blit(sprite.image, sprite.rect)