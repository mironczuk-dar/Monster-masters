#IMPORTING LIBRARIES
import pygame

def draw_bar(window, rect, value, max_value, colour, bg_colour, radius = 1):
    ratio = rect.width / max_value
    bg_rect = rect.copy()
    progress = max(0, min(rect.width, value*ratio))
    progress_rect = pygame.FRect(rect.topleft, (progress, rect.height))

    pygame.draw.rect(window, bg_colour, bg_rect, 0, radius)
    pygame.draw.rect(window, colour, progress_rect, 0, radius)
    