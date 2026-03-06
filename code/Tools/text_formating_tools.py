#IMPORTING LIBRARIES
import pygame

def create_text_with_outline(text, font, text_color, outline_color, outline_width=2):
    text_surf = font.render(text, False, text_color).convert_alpha()
    outline_surf = font.render(text, False, outline_color).convert_alpha()
    
    w = text_surf.get_width() + 2 * outline_width
    h = text_surf.get_height() + 2 * outline_width
    

    final_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    final_surf = final_surf.convert_alpha()
    
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                final_surf.blit(outline_surf, (outline_width + dx, outline_width + dy))
                
    final_surf.blit(text_surf, (outline_width, outline_width))
    
    return final_surf