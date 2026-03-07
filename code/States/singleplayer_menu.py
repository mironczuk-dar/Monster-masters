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

        y_offset = 220
        folders = sorted(os.listdir(s.saves_dir))

        for folder in folders:
            full_path = join(s.saves_dir, folder)
            manifest_path = join(full_path, "manifest.json")
            trainer_path = join(full_path, "trainer.json")
            party_path = join(full_path, "party.json")
            world_data = join(full_path, "world.json")

            if not os.path.isdir(full_path) or not os.path.exists(manifest_path):
                continue

            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)

                world_data_loaded = {}
                if os.path.exists(world_data):
                    with open(world_data, "r") as f:
                        world_data_loaded = json.load(f)

                # SAFE LOAD trainer
                trainer_data = {}
                if os.path.exists(trainer_path):
                    with open(trainer_path, "r") as f:
                        trainer_data = json.load(f)

                # SAFE LOAD party
                party_data = {}
                if os.path.exists(party_path):
                    with open(party_path, "r") as f:
                        party_data = json.load(f)

                if s.delete_mode:
                    action = lambda p=full_path: s.delete_save(p)
                else:
                    action = lambda p=full_path: s.select_save(p)

                s.save_buttons.append(
                    SaveFileLog(
                        s.game,
                        pos=(WINDOW_WIDTH // 2, y_offset),
                        save_path=full_path,
                        manifest=manifest,
                        world_data=world_data_loaded,
                        trainer_data=trainer_data,
                        party_data=party_data,
                        delete_mode=s.delete_mode,
                        action=action
                    )
                )

                y_offset += 220

            except Exception as e:
                print(f"Failed to load save {folder}: {e}")

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


class SaveFileLog:
    def __init__(s, game, pos, save_path, manifest, world_data, trainer_data, party_data, delete_mode, action):
        s.game = game
        s.save_path = save_path
        s.manifest = manifest
        s.world_data = world_data
        s.trainer_data = trainer_data
        s.party_data = party_data
        s.delete_mode = delete_mode
        s.action = action

        s.width = int(WINDOW_WIDTH * 0.8)
        s.height = 200

        s.image = pygame.Surface((s.width, s.height), pygame.SRCALPHA)
        s.rect = s.image.get_rect(center=pos)

        s.hover = False

        # Extract data
        s.name = manifest.get("slot_name", "Unknown")
        s.badges = manifest.get("badges", 0)
        s.location = world_data.get("current_map", "Unknown")

        s.gender = trainer_data.get("gender", "male")

    def draw(s, window):
        s.image.fill((0,0,0,0))

        # Background color
        if s.delete_mode:
            bg = (120, 30, 30)
        elif s.hover:
            bg = (70, 90, 160)
        else:
            bg = (50, 60, 120)

        pygame.draw.rect(s.image, bg, (0,0,s.width,s.height), border_radius=12)

        # --- TRAINER ICON ---
        trainer_icon = s.get_trainer_icon()
        s.image.blit(trainer_icon, (20, s.height//2 - trainer_icon.get_height()//2))

        # --- TEXT ---
        fonts = s.game.save_file_log_fonts

        name_surf = fonts['big'].render(s.name, True, (255, 255, 255))
        badges_surf = fonts['medium'].render(f"Badges: {s.badges}", True, (220, 220, 220))
        location_surf = fonts['small'].render(s.location, True, (200, 200, 200))

        s.image.blit(name_surf, (180, 25))
        s.image.blit(badges_surf, (180, 100))
        s.image.blit(location_surf, (180, 140))

        # --- PARTY ICONS ---
        s.draw_party_icons()

        window.blit(s.image, s.rect)

    def draw_party_icons(s):
        x = s.width - 700
        y = s.height * 0.5

        for monster in s.party_data.get("slots", []):

            center_pos = (x, y)

            if monster is None:
                empty_rect = pygame.Rect(0, 0, 40, 40)
                empty_rect.center = center_pos

                pygame.draw.rect(
                    s.image,
                    (80, 80, 80),
                    empty_rect,
                    border_radius=6
                )
            else:
                name = monster.get("name")
                icon = s.get_monster_icon(name)

                icon_rect = icon.get_rect(center=center_pos)
                s.image.blit(icon, icon_rect)

            x += 150

    def get_trainer_icon(s):
        if s.gender == "male":
            return s.game.overworld_frames["characters"]["player_male"]['down'][0]
        else:
            return s.game.overworld_frames["characters"]["player_female"]['down'][0]       
    def handling_events(s, events):
        mouse_pos = s.game.get_scaled_mouse_pos()

        s.hover = s.rect.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if s.hover:
                    s.game.audio_manager.play_sound(s.game.select_sound)
                    s.action()

    def update(s, delta_time):
        mouse_pos = s.game.get_scaled_mouse_pos()
        s.hover = s.rect.collidepoint(mouse_pos)

    def get_monster_icon(s, monster_name):
        try:
            return s.game.monster_icons[monster_name]
        except:
            # fallback icon
            return pygame.Surface((40, 40), pygame.SRCALPHA)