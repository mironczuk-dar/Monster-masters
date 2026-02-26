#IMPORTING LIBRAIES
import pygame

#IMPORTING ELEMENTS
from Singleplayer.battle_sprites import TimedSprite

#IMPORTING FILES
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from Singleplayer.singleplayer_settings import COLORS

class DeathScreen:
    def __init__(s, game, singleplayer, image, save_file):

        s.game = game
        s.singleplayer = singleplayer

        s.image = image
        s.all_sprites = pygame.sprite.Group()


        s.message = s.game.battle_fonts['regular'].render("All your monsters were defeated. Better luck next time!", False, COLORS['red'])
        TimedSprite(s.all_sprites, (WINDOW_WIDTH/2, WINDOW_HEIGHT - s.message.height - 50), s.message, 1000)

        s.input_message = s.game.battle_fonts['regular'].render("Press any button to continue", False, COLORS['red'])
        TimedSprite(s.all_sprites, (WINDOW_WIDTH/2, WINDOW_HEIGHT - s.input_message.height - 5), s.input_message, 1000)


    def draw(s, window):
        window.blit(s.image, (0,0))

        s.all_sprites.draw(window)

    def update(s, delta_time):
        s.all_sprites.update(delta_time)

    def handling_events(s, events):
        controlls = s.game.controlls_data

        keys = pygame.key.get_just_pressed()

        for event in events:
            if event.type == pygame.KEYDOWN:
                s.singleplayer.delete_save_file()

