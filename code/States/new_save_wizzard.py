import pygame
from os.path import join
from os import makedirs

from States.generic_state import BaseState
from UI_elements.buttons import GenericButton
from settings import WINDOW_WIDTH, BASE_DIR

class NewSaveWizard(BaseState):
    def __init__(s, game):
        super().__init__(game)
        s.step = "NAME_INPUT"  # Steps: NAME_INPUT -> GENDER_SELECT
        s.trainer_name = ""
        s.gender = None  # Initially no gender selected
        s.font = pygame.font.SysFont("Arial", 32)

        # UI Elements
        s.buttons = []
        s.confirm_enabled = False  # Track confirm button state manually
        s.setup_ui()

    def setup_ui(s):
        """Set up buttons depending on the current step"""
        s.buttons.clear()
        if s.step == "NAME_INPUT":
            s.confirm_enabled = bool(s.trainer_name)
            s.confirm_button = GenericButton(
                s.game, (200, 50), (WINDOW_WIDTH//2, 500), "Confirm",
                colour=(80, 160, 80), action=s.next_step
            )
            s.buttons.append(s.confirm_button)
        elif s.step == "GENDER_SELECT":
            s.confirm_enabled = s.gender in ["male", "female"]
            s.buttons.append(
                GenericButton(s.game, (180, 50), (WINDOW_WIDTH//2 - 120, 400), "Male",
                              colour=(80, 160, 220), action=lambda: s.set_gender("male"))
            )
            s.buttons.append(
                GenericButton(s.game, (180, 50), (WINDOW_WIDTH//2 + 120, 400), "Female",
                              colour=(220, 100, 160), action=lambda: s.set_gender("female"))
            )
            s.confirm_button = GenericButton(
                s.game, (200, 50), (WINDOW_WIDTH//2, 500), "Confirm",
                colour=(80, 160, 80), action=s.next_step
            )
            s.buttons.append(s.confirm_button)

    def set_gender(s, gender):
        s.gender = gender
        print(f"Selected gender: {gender}")
        s.confirm_enabled = True  # Now Confirm is enabled

    def next_step(s):
        if not s.confirm_enabled:
            return  # Ignore clicks if confirm is disabled
        if s.step == "NAME_INPUT" and s.trainer_name:
            s.step = "GENDER_SELECT"
            s.setup_ui()
        elif s.step == "GENDER_SELECT" and s.gender:
            s.finish_and_create()

    def finish_and_create(s):
        saves_dir = join(BASE_DIR, 'data', 'saves')
        save_folder = join(saves_dir, f"Save_{s.trainer_name}_{pygame.time.get_ticks()}")
        s.create_files(save_folder)
        s.step = "NAME_INPUT"
        s.trainer_name = ""
        s.setup_ui()
        s.game.state_manager.change_state('Singleplayer menu')

    def create_files(s, save_folder):
        from Manifest.save_file_manifest import (
            DEFAULT_SAVE_FILE_MANIFEST,
            DEFAULT_TRAINER,
            DEFAULT_PARTY,
            DEFAULT_PC,
            DEFAULT_WORLD,
            DEFAULT_FLAGS,
            DEFAULT_INVENTORY
        )
        from Tools.data_loading_tools import save_data

        makedirs(save_folder, exist_ok=True)

        # --- MANIFEST ---
        manifest = DEFAULT_SAVE_FILE_MANIFEST.copy()
        manifest["slot_name"] = s.trainer_name

        # --- TRAINER (TO TU MUSI BYĆ GENDER) ---
        trainer = DEFAULT_TRAINER.copy()
        trainer["name"] = s.trainer_name
        trainer["gender"] = s.gender

        files_to_create = {
            "manifest.json": manifest,
            "trainer.json": trainer,   # <-- używamy zmodyfikowanego
            "party.json": DEFAULT_PARTY,
            "pc.json": DEFAULT_PC,
            "world.json": DEFAULT_WORLD,
            "flags.json": DEFAULT_FLAGS,
            "inventory.json": DEFAULT_INVENTORY
        }

        for filename, data in files_to_create.items():
            save_data(data, join(save_folder, filename))

    def handling_events(s, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if s.step == "NAME_INPUT":
                    if event.key == pygame.K_BACKSPACE:
                        s.trainer_name = s.trainer_name[:-1]
                    elif len(s.trainer_name) < 12:
                        s.trainer_name += event.unicode
                    # Update confirm enabled state
                    s.confirm_enabled = bool(s.trainer_name)

        for b in s.buttons:
            # Manually ignore confirm click if disabled
            if b == s.confirm_button and not s.confirm_enabled:
                continue
            b.handling_events(events)

    def update(s, delta_time):
        for b in s.buttons:
            b.update(delta_time)

    def draw(s, window):
        window.fill((30, 30, 50))
        
        if s.step == "NAME_INPUT":
            s.draw_text(window, "Enter Your Name:", (WINDOW_WIDTH//2, 200))
            s.draw_text(window, s.trainer_name + "_", (WINDOW_WIDTH//2, 300), colour=(255, 255, 0))
        elif s.step == "GENDER_SELECT":
            s.draw_text(window, "Select Gender:", (WINDOW_WIDTH//2, 300))
            if s.gender:
                s.draw_text(window, f"Selected: {s.gender.capitalize()}", (WINDOW_WIDTH//2, 350), colour=(255, 255, 0))
        
        # Inside NewSaveWizard.draw
        for b in s.buttons:
            if b == s.confirm_button and not s.confirm_enabled:
                b.image.set_alpha(100) # Dim it
                b.draw(window)
                b.image.set_alpha(255) # Reset for next frame
            else:
                b.draw(window)

    def draw_text(s, window, text, pos, colour=(255, 255, 255)):
        txt_surf = s.font.render(text, True, colour)
        rect = txt_surf.get_rect(center=pos)
        window.blit(txt_surf, rect)