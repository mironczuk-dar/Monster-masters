#IMPORTING LIBRARIES
import pygame
from Singleplayer.singleplayer_settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(s, groups, pos, surface, level_depth = WORLD_LAYERS['main']):
        super().__init__(groups)

        s.image = surface
        s.rect = s.image.get_frect(topleft = pos)
        s.level_depth = level_depth
        s.hitbox = s.rect.copy()

class PortalSprite(Sprite):
    def __init__(s, groups, pos, size, target):
        surface = pygame.Surface(size)
        super().__init__(groups, pos, surface)
        s.target = target

class TreeSprite(Sprite):
    def __init__(s, groups, pos, surface, level_depth = WORLD_LAYERS['main']):
        super().__init__(groups, pos, surface, level_depth)
        s.hitbox = s.rect.inflate(-33, -s.rect.height*0.78)
        s.hitbox.centery = s.rect.centery + 77

    def draw(s, window, offset):
        # Rysowanie samej postaci
        window.blit(s.image, s.rect.topleft - offset)
        
        # Rysowanie hitboxa (z tym samym offsetem!)
        hitbox_rect = s.hitbox.copy()
        hitbox_rect.topleft -= offset
        pygame.draw.rect(window, (255, 0, 0), hitbox_rect, 2)

class SmallTreeSprite(Sprite):
    def __init__(s, groups, pos, surface, level_depth = WORLD_LAYERS['main']):
        super().__init__(groups, pos, surface, level_depth)
        s.hitbox = s.rect.inflate(-5, -s.rect.height*0.73)
        s.hitbox.centery = s.rect.centery + 50

    def draw(s, window, offset):
        # Rysowanie samej postaci
        window.blit(s.image, s.rect.topleft - offset)
        
        # Rysowanie hitboxa (z tym samym offsetem!)
        hitbox_rect = s.hitbox.copy()
        hitbox_rect.topleft -= offset
        pygame.draw.rect(window, (255, 0, 0), hitbox_rect, 2)

class HouseSprite(Sprite):
    def __init__(s, groups, pos, surface, level_depth = WORLD_LAYERS['main']):
        super().__init__(groups, pos, surface, level_depth)
        s.hitbox = s.rect.inflate(0, -s.rect.height*0.4)
        s.hitbox.bottom = s.rect.bottom

    def draw(s, window, offset):
        # Rysowanie samej postaci
        window.blit(s.image, s.rect.topleft - offset)

        # Rysowanie hitboxa (z tym samym offsetem!)
        hitbox_rect = s.hitbox.copy()
        hitbox_rect.topleft -= offset
        pygame.draw.rect(window, (255, 0, 0), hitbox_rect, 2)

class MapWall(Sprite):
    def __init__(s, groups, pos, surface):
        super().__init__(groups, pos, surface)
        s.hitbox = s.rect.copy()
    
class GrassPatchSprite(Sprite):
    def __init__(s, groups, pos, surface, biome, level_depth = WORLD_LAYERS['main']):
        super().__init__(groups, pos, surface, level_depth)
        s.biome = biome

    def depth_anchor(self):
        return self.rect.bottom - 10

class AnimatedSprite(Sprite):
    def __init__(s, groups, pos, frames, level_depth = WORLD_LAYERS['main']):

        s.frames = frames
        s.frame_index = 0

        super().__init__(groups, pos, frames[s.frame_index], level_depth)

    def update(s, delta_time):
        s.frame_index += ANIMATION_SPEED * delta_time
        s.image = s.frames[int(s.frame_index % len(s.frames))]

