#IMPORTING LIBRAIES
import pygame
from pygame.math import Vector2 as vector


def scale_asset(asset, scale_factor):
    
    if isinstance(asset, pygame.Surface):
        new_size = (int(asset.get_width() * scale_factor), int(asset.get_height() * scale_factor))
        return pygame.transform.scale(asset, new_size)
    
    elif isinstance(asset, list):
        return [scale_asset(item, scale_factor) for item in asset]
    
    elif isinstance(asset, dict):
        return {key: scale_asset(value, scale_factor) for key, value in asset.items()}
    
    return asset


def outline_creator(frame_dict, width):
    def process_surface(surface, w):
        mask = pygame.mask.from_surface(surface)
        outline_surf = mask.to_surface(setcolor='white', unsetcolor=(0,0,0,0))
        
        new_size = vector(surface.get_size()) + vector(w * 2, w * 2)
        new_surf = pygame.Surface(new_size, pygame.SRCALPHA)
        
        for dx, dy in [(-w, 0), (w, 0), (0, -w), (0, w), (-w, -w), (w, -w), (-w, w), (w, w)]:
            new_surf.blit(outline_surf, (w + dx, w + dy))
        
        new_surf.blit(surface, (w, w))
        
        return new_surf

    out_dict = {}
    for key, value in frame_dict.items():
        if isinstance(value, dict):
            out_dict[key] = {}
            for state, frames in value.items():
                out_dict[key][state] = [process_surface(f, width) for f in frames]
        else:
            out_dict[key] = process_surface(value, width)
            
    return out_dict

