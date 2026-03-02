import pygame
from os.path import join
from os import makedirs

from States.generic_state import BaseState
from UI_elements.buttons import GenericButton
from UI_elements.keyboard import Keyboard
from settings import WINDOW_WIDTH, BASE_DIR, WINDOW_HEIGHT


class NewSaveWizard(BaseState):
    def __init__(s, game):
        super().__init__(game)

        # STEPS: NAME_INPUT -> GENDER_SELECT
        s.step = "NAME_INPUT"

        s.trainer_name = ""
        s.gender = None

        s.font = pygame.font.SysFont("Arial", 42)

        # UI
        s.buttons = []
        s.confirm_enabled = False
        s.confirm_button = None

        # Keyboard
        keyboard_pos = (100, 400)
        keyboard_size = (WINDOW_WIDTH - 2 * keyboard_pos[0], WINDOW_HEIGHT - keyboard_pos[1] - 100)
        s.keyboard = Keyboard(
            s.game,
            pos = keyboard_pos,
            size = keyboard_size,
            max_length=12
        )

        s.setup_ui()

    # ==============================
    # UI SETUP
    # ==============================
    def setup_ui(s):
        s.buttons.clear()

        if s.step == "NAME_INPUT":
            s.confirm_enabled = bool(s.trainer_name)

            s.confirm_button = GenericButton(
                s.game,
                (200, 50),
                (WINDOW_WIDTH // 2, 320),
                "Confirm",
                colour=(80, 160, 80),
                action=s.next_step
            )
            s.buttons.append(s.confirm_button)

        elif s.step == "GENDER_SELECT":
            s.confirm_enabled = s.gender in ["male", "female"]

            s.buttons.append(
                GenericButton(
                    s.game,
                    (180, 50),
                    (WINDOW_WIDTH // 2 - 120, 400),
                    "Male",
                    colour=(80, 160, 220),
                    action=lambda: s.set_gender("male")
                )
            )

            s.buttons.append(
                GenericButton(
                    s.game,
                    (180, 50),
                    (WINDOW_WIDTH // 2 + 120, 400),
                    "Female",
                    colour=(220, 100, 160),
                    action=lambda: s.set_gender("female")
                )
            )

            s.confirm_button = GenericButton(
                s.game,
                (200, 50),
                (WINDOW_WIDTH // 2, 520),
                "Confirm",
                colour=(80, 160, 80),
                action=s.next_step
            )
            s.buttons.append(s.confirm_button)

    # ==============================
    # STEP LOGIC
    # ==============================
    def set_gender(s, gender):
        s.gender = gender
        s.confirm_enabled = True

    def next_step(s):
        if not s.confirm_enabled:
            return

        if s.step == "NAME_INPUT" and s.trainer_name:
            s.step = "GENDER_SELECT"
            s.setup_ui()

        elif s.step == "GENDER_SELECT" and s.gender:
            s.finish_and_create()

    # ==============================
    # SAVE CREATION
    # ==============================
    def finish_and_create(s):
        saves_dir = join(BASE_DIR, 'data', 'saves')
        save_folder = join(
            saves_dir,
            f"Save_{s.trainer_name}_{pygame.time.get_ticks()}"
        )

        s.create_files(save_folder)

        # RESET WIZARD
        s.step = "NAME_INPUT"
        s.trainer_name = ""
        s.gender = None
        s.keyboard.text = ""
        s.keyboard.grid_pos = [0, 0]
        s.keyboard.finished = False

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

        manifest = DEFAULT_SAVE_FILE_MANIFEST.copy()
        manifest["slot_name"] = s.trainer_name

        trainer = DEFAULT_TRAINER.copy()
        trainer["name"] = s.trainer_name
        trainer["gender"] = s.gender

        files_to_create = {
            "manifest.json": manifest,
            "trainer.json": trainer,
            "party.json": DEFAULT_PARTY,
            "pc.json": DEFAULT_PC,
            "world.json": DEFAULT_WORLD,
            "flags.json": DEFAULT_FLAGS,
            "inventory.json": DEFAULT_INVENTORY
        }

        for filename, data in files_to_create.items():
            save_data(data, join(save_folder, filename))

    # ==============================
    # EVENT HANDLING
    # ==============================
    def handling_events(s, events):

        # KEYBOARD ONLY IN NAME STEP
        if s.step == "NAME_INPUT":
            s.keyboard.handling_events(events)

        # BUTTONS
        for b in s.buttons:
            if b == s.confirm_button and not s.confirm_enabled:
                continue
            b.handling_events(events)

    # ==============================
    # UPDATE
    # ==============================
    def update(s, delta_time):

        if s.step == "NAME_INPUT":
            s.trainer_name = s.keyboard.text
            s.confirm_enabled = bool(s.trainer_name)

            if s.keyboard.finished:
                s.next_step()
                s.keyboard.finished = False

    # ==============================
    # DRAW
    # ==============================
    def draw(s, window):
        window.fill((30, 30, 50))

        if s.step == "NAME_INPUT":
            s.draw_text(window, "Enter Your Name:", (WINDOW_WIDTH // 2, 100))
            max_len = s.keyboard.max_length
            name = s.trainer_name

            # Tworzymy tekst stałej długości
            display_name = name + "-" * (max_len - len(name))

            s.draw_text(
                window,
                display_name,
                (WINDOW_WIDTH // 2, 200),
                colour=(255, 255, 0)
            )

            # DRAW KEYBOARD
            s.keyboard.draw(
                window
            )

        elif s.step == "GENDER_SELECT":
            s.draw_text(window, "Select Gender:", (WINDOW_WIDTH // 2, 300))

            if s.gender:
                s.draw_text(
                    window,
                    f"Selected: {s.gender.capitalize()}",
                    (WINDOW_WIDTH // 2, 350),
                    colour=(255, 255, 0)
                )

        # DRAW BUTTONS
        for b in s.buttons:
            if b == s.confirm_button and not s.confirm_enabled:
                b.image.set_alpha(100)
                b.draw(window)
                b.image.set_alpha(255)
            else:
                b.draw(window)

    # ==============================
    # TEXT DRAW HELPER
    # ==============================
    def draw_text(s, window, text, pos, colour=(255, 255, 255)):
        txt_surf = s.font.render(text, True, colour)
        rect = txt_surf.get_rect(center=pos)
        window.blit(txt_surf, rect)