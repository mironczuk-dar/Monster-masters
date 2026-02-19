import os
import shutil
from os.path import join
import json
import pygame

from States.generic_state import BaseState
from UI_elements.buttons import GenericButton, ToggleButton
from settings import BASE_DIR, WINDOW_WIDTH
from Manifest.save_file_manifest import *
from Tools.data_loading_tools import save_data
from States.singleplayer import Singleplayer




class SingleplayerMenu(BaseState):
    def __init__(s, game):
        super().__init__(game)
        s.save_buttons = []
        s.menu_buttons = []
        s.delete_mode = False
        s.saves_dir = join(BASE_DIR, 'data', 'saves')

    def on_enter(s):
        s.delete_mode = False
        s.create_menu_buttons()
        s.load_saves()

    def create_menu_buttons(s):
        s.menu_buttons = [
            # BACK BUTTON
            GenericButton(
                s.game, size=(180, 50), pos=(110, 40), text="<< Back",
                colour=(160, 80, 80),
                action=lambda: s.game.state_manager.change_state('Start menu')
            ),
            # NEW SAVE BUTTON
            GenericButton(
                s.game, size=(200, 50), pos=(WINDOW_WIDTH - 140, 40), text="+ New Save",
                colour=(80, 160, 80),
                action=s.new_save
            ),
            # DELETE MODE TOGGLE
            ToggleButton(
                s.game, size=(220, 50), pos=(WINDOW_WIDTH // 2, 40), text="Delete Mode",
                active_colour=(200, 60, 60), inactive_colour=(80, 80, 80),
                action=s.toggle_delete_mode
            )
        ]

    def toggle_delete_mode(s):
        s.delete_mode = not s.delete_mode
        s.load_saves()

    def load_saves(s):
        s.save_buttons.clear()
        if not os.path.exists(s.saves_dir):
            os.makedirs(s.saves_dir)

        y_offset = 150
        # Sort folders by name or date so they don't jump around
        folders = sorted(os.listdir(s.saves_dir))

        for folder in folders:
            full_path = join(s.saves_dir, folder)
            manifest_path = join(full_path, "manifest.json")

            if not os.path.isdir(full_path) or not os.path.exists(manifest_path):
                continue

            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)

                save_name = manifest.get("slot_name", folder)
                badges = manifest.get("badges", 0)
                location = manifest.get("location", "Unknown")
                text = f"{save_name} | Badges: {badges} | {location}"

                if s.delete_mode:
                    colour = (220, 40, 40)
                    # We pass 'full_path' into the lambda's default arg to freeze its value
                    action = lambda p=full_path: s.delete_save(p)
                else:
                    colour = (60, 100, 180)
                    action = lambda p=full_path: s.select_save(p)

                s.save_buttons.append(GenericButton(
                    s.game, size=(600, 65), pos=(WINDOW_WIDTH // 2, y_offset),
                    text=text, colour=colour, action=action
                ))
                y_offset += 85
            except Exception as e:
                print(f"Failed to load manifest in {folder}: {e}")

    def select_save(s, path):
        print(f"Loading: {path}")
        s.game.state_manager.add_state("Singleplayer", Singleplayer(s.game, path))
        s.game.state_manager.change_state("Singleplayer")

    def delete_save(s, path):
        try:
            shutil.rmtree(path)
            print(f"Deleted: {path}")
            s.load_saves() # Refresh list
        except Exception as e:
            print(f"Error deleting save: {e}")

    def create_new_save(s, save_folder, slot_name):
        os.makedirs(save_folder, exist_ok=True)
        
        # Correctly referencing your dictionary names
        manifest = DEFAULT_SAVE_FILE_MANIFEST.copy()
        manifest["slot_name"] = slot_name

        # Mapping data to filenames
        files_to_create = {
            "manifest.json": manifest,
            "trainer.json": DEFAULT_TRAINER,
            "party.json": DEFAULT_PARTY,
            "pc.json": DEFAULT_PC,
            "world.json": DEFAULT_WORLD,
            "flags.json": DEFAULT_FLAGS,
            "inventory.json": DEFAULT_INVENTORY
        }

        for filename, data in files_to_create.items():
            save_data(data, join(save_folder, filename))

    def new_save(s):
        s.game.state_manager.change_state("New save wizzard")

    def handling_events(s, events):
        for b in s.menu_buttons + s.save_buttons:
            b.handling_events(events)

    def update(s, delta_time):
        for b in s.menu_buttons + s.save_buttons:
            b.update(delta_time)

    def draw(s, window):
        # Visual feedback for delete mode
        bg_color = (40, 20, 20) if s.delete_mode else (25, 25, 40)
        window.fill(bg_color)

        for b in s.menu_buttons + s.save_buttons:
            b.draw(window)
            
        # Optional: Title text
        # s.game.draw_text("Select Save File", size=32, pos=(WINDOW_WIDTH//2, 100))