#IMPORITNG LIBRARIES
from settings import *


# FUNCTION FOR DRAWING FPS TO PLAYER SCREEN
def draw_fps_counter(game, pos=(10, None), color=(0, 100, 0)):

    #OLNY DRAWING THE FPS IF THE OPTION IS ENABLED
    if not game.window_data.get('show_fps', False):
        return

    #POSITION OF THE COUNTER AT THE BOTTOM IF ATTRIBUTES NOT GIVEN
    if pos[1] is None:
        pos = (pos[0], game.window.get_height() - 45)

    #RENDERING FPS
    font = pygame.font.SysFont(None, 40)
    fps = int(game.clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, color)
    game.window.blit(fps_text, pos)