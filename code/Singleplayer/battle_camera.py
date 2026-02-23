#IMPORTING LIBRARIES
import pygame

#IMPORTING FILES
from Singleplayer.singleplayer_settings import BATTLE_LAYERS

class BattleSprites(pygame.sprite.Group):
    def __init__(s, game):
        super().__init__()

        s.game = game

    def draw(s, window, current_monster_sprite, side, mode, target_index, player_sprites, opponent_sprites):
        target_monster_sprite = None
        if mode == 'target':
            sprite_group = opponent_sprites if side == 'opponent' else player_sprites
            sprites_list = sprite_group.sprites()
            
            if 0 <= target_index < len(sprites_list):
                target_monster_sprite = sprites_list[target_index]

        for sprite in sorted(s, key=lambda sprite: sprite.z):
            if sprite.z == BATTLE_LAYERS['outline']:
                if hasattr(sprite, 'monster_sprite'):
                    is_current = sprite.monster_sprite == current_monster_sprite and not (mode == 'target' and side == 'player')
                    is_target = target_monster_sprite and sprite.monster_sprite == target_monster_sprite
                    
                    if is_current or is_target:
                        window.blit(sprite.image, sprite.rect)
            else:
                window.blit(sprite.image, sprite.rect)