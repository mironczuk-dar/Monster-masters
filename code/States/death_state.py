# IMPORTING LIBRARIES
import pygame
import math

# IMPORTING FILES
from States.generic_state import BaseState
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from Singleplayer.singleplayer_settings import COLORS


class DeathState(BaseState):

    def __init__(s, game, save_path, death_image=None):
        super().__init__(game)

        s.game = game
        s.save_path = save_path

        # animacja fade
        s.alpha = 0
        s.fade_speed = 300

        # lekki ruch tekstu
        s.title_offset = 20
        s.blink_timer = 0

        # fonty
        s.title_font = s.game.death_state_fonts['big']
        s.text_font = s.game.death_state_fonts['regular']

        # tło (ciemny overlay zamiast obrazka)
        s.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        s.background.fill((10, 10, 20))

    # -------------------------------------------------

    def update(s, delta_time):

        # FADE IN
        if s.alpha < 200:
            s.alpha += s.fade_speed * delta_time
            if s.alpha > 200:
                s.alpha = 200

        # delikatne unoszenie tytułu
        s.title_offset = 20 - math.sin(pygame.time.get_ticks() * 0.003) * 8

        # miganie tekstu
        s.blink_timer += delta_time

    # -------------------------------------------------

    def draw(s, window):

        # tło
        window.blit(s.background, (0, 0))

        # overlay z fade
        fade_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fade_overlay.set_alpha(int(s.alpha))
        fade_overlay.fill((0, 0, 0))
        window.blit(fade_overlay, (0, 0))

        # ---------- TITLE ----------
        title_text = "GAME OVER"

        title_surface = s.title_font.render(
            title_text,
            True,
            COLORS['red']
        )

        title_rect = title_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80 + s.title_offset)
        )

        window.blit(title_surface, title_rect)

        # ---------- SUB TEXT ----------
        sub_text = "All your monsters were defeated"

        sub_surface = s.text_font.render(
            sub_text,
            True,
            (220, 220, 230)
        )

        sub_rect = sub_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20)
        )

        window.blit(sub_surface, sub_rect)

        # ---------- PRESS ANY KEY ----------
        if int(s.blink_timer * 2) % 2 == 0:

            press_text = "Press any key to return to menu"

            press_surface = s.text_font.render(
                press_text,
                True,
                (150, 150, 170)
            )

            press_rect = press_surface.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)
            )

            window.blit(press_surface, press_rect)

    # -------------------------------------------------

    def handling_events(s, events):

        for event in events:

            if event.type == pygame.KEYDOWN:

                # usuń save
                s.delete_save()

                # wróć do menu
                s.game.state_manager.change_state("Start menu")

    # -------------------------------------------------

    def delete_save(s):
        import shutil
        import os

        if os.path.isdir(s.save_path):
            shutil.rmtree(s.save_path)

        print("Save deleted.")

    def on_enter(s):
        s.game.audio_manager.play_sound(s.game.death_state_sound)