import pygame

def scale_asset(asset, scale_factor):
    
    if isinstance(asset, pygame.Surface):
        new_size = (int(asset.get_width() * scale_factor), int(asset.get_height() * scale_factor))
        return pygame.transform.scale(asset, new_size)
    
    elif isinstance(asset, list):
        return [scale_asset(item, scale_factor) for item in asset]
    
    elif isinstance(asset, dict):
        return {key: scale_asset(value, scale_factor) for key, value in asset.items()}
    
    return asset