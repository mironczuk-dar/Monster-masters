import os
import shutil
import math
import json
import pygame
from os.path import join

from States.generic_state import BaseState
from UI_elements.buttons import GenericButton, ImageAudioButton, ImageToggleButton
from settings import BASE_DIR, WINDOW_WIDTH
from Manifest.save_file_manifest import *
from States.singleplayer import Singleplayer

#IMPORTING TOOLS
from Tools.game_elemet_importing_machine import import_image
from Tools.data_loading_tools import save_data

class SingleplayerMenu(BaseState):
    def __init__(s, game):
        super().__init__(game)
        s.save_buttons = []
        s.menu_buttons = []
        s.active_index_menu = 'saves' #OR UI BUTTONS
        s.active_index = 0
        s.delete_mode = False
        s.saves_dir = join(BASE_DIR, 'data', 'saves')
        
        s.bg_color = pygame.Color(25, 25, 40)
        s.target_bg_color = pygame.Color(25, 25, 40)

    def get_all_buttons(s):
        return s.menu_buttons + s.save_buttons

    def on_enter(s):
        s.delete_mode = False
        s.active_index_menu = 'saves'
        s.active_index = 0
        s.target_bg_color = pygame.Color(25, 25, 40)
        s.create_menu_buttons()
        s.load_saves()

    def create_menu_buttons(s):
        size = 100
        path = join(BASE_DIR, 'assets', 'singleplayer_menu_assets')
        
        # --- 1. PRZYCISK BACK (Lewy górny róg) ---
        raw_back = import_image(join(path, 'back_button'))
        raw_hover = import_image(join(path, 'back_button_hovered'))
        scale_ratio = size / raw_back.get_width()
        
        back_button = pygame.transform.scale_by(raw_back, scale_ratio)
        back_button_hover = pygame.transform.scale_by(raw_hover, scale_ratio)

        # --- 2. ŁADOWANIE I SKALOWANIE (New Save & Delete Mode) ---
        # Używamy tej samej skali dla obu, aby były identycznej wysokości
        raw_save = import_image(join(path, 'new_save_file_button'))
        raw_save_hover = import_image(join(path, 'new_save_file_button_hovered'))
        
        save_scale = 120 / raw_save.get_height() 
        
        # Grafiki New Save
        save_img = pygame.transform.scale_by(raw_save, save_scale)
        save_img_hover = pygame.transform.scale_by(raw_save_hover, save_scale)

        # Grafiki Delete Mode (stosujemy save_scale!)
        raw_del_off = import_image(join(path, 'delete_mode_button'))
        raw_del_hover = import_image(join(path, 'delete_mode_button_hovered'))
        raw_del_on = import_image(join(path, 'delete_mode_button_selected'))

        del_off = pygame.transform.scale_by(raw_del_off, save_scale)
        del_hover = pygame.transform.scale_by(raw_del_hover, save_scale)
        del_on = pygame.transform.scale_by(raw_del_on, save_scale)

        # --- 3. POZYCJONOWANIE (Prawy górny róg) ---
        margin = 30
        spacing = 20 # Odstęp między przyciskami
        
        # Obliczamy pozycję od prawej strony
        # Najpierw Delete Mode (najbardziej na prawo)
        delete_pos_x = WINDOW_WIDTH - (del_off.get_width() // 2) - margin
        delete_pos = (delete_pos_x, 70)
        
        # Potem New Save (na lewo od Delete Mode)
        save_pos_x = delete_pos_x - (del_off.get_width() // 2) - (save_img.get_width() // 2) - spacing
        save_pos = (save_pos_x, 70)

        s.menu_buttons = [
            # Przycisk POWRÓT
            ImageAudioButton(
                s.game, 
                pos=(back_button.get_width() // 2 + 20, back_button.get_height() // 2 + 20),
                image=back_button,
                hover_image=back_button_hover,
                sound=s.game.select_sound,
                action=lambda: s.game.state_manager.change_state('Start menu'),
                wait_for_sound_to_end=False
            ),
            # Przycisk NEW SAVE
            ImageAudioButton(
                s.game,
                pos=save_pos,
                image=save_img,
                text="New Save",
                font=join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'),
                hover_image=save_img_hover,
                sound=s.game.select_sound,
                action=s.new_save
            ),
            # Przycisk DELETE TOGGLE
            ImageToggleButton(
                s.game,
                pos=delete_pos,
                idle_img=del_off,
                hover_img=del_hover,
                active_img=del_on,
                action=s.toggle_delete_mode,
                text="Delete Mode",
                font_path=join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf')
            )
        ]

    def toggle_delete_mode(s):
        s.delete_mode = not s.delete_mode
        s.target_bg_color = pygame.Color(50, 20, 20) if s.delete_mode else pygame.Color(25, 25, 40)
        s.load_saves()

    def load_saves(s):
        s.save_buttons.clear()
        if not os.path.exists(s.saves_dir): os.makedirs(s.saves_dir)

        y_offset = 240
        folders = sorted(os.listdir(s.saves_dir))

        for folder in folders:
            full_path = join(s.saves_dir, folder)
            manifest_path = join(full_path, "manifest.json")
            if not os.path.isdir(full_path) or not os.path.exists(manifest_path): continue

            try:
                with open(manifest_path, "r") as f: manifest = json.load(f)
                
                # Wczytywanie dodatkowych danych z obsługą błędów
                def safe_load(filename):
                    p = join(full_path, filename)
                    if os.path.exists(p):
                        with open(p, "r") as f: return json.load(f)
                    return {}

                world_data = safe_load("world.json")
                trainer_data = safe_load("trainer.json")
                party_data = safe_load("party.json")

                action = (lambda p=full_path: s.delete_save(p)) if s.delete_mode else (lambda p=full_path: s.select_save(p))

                s.save_buttons.append(
                    SaveFileLog(
                        s.game,
                        pos=(WINDOW_WIDTH // 2, y_offset),
                        save_path=full_path,
                        manifest=manifest,
                        world_data=world_data,
                        trainer_data=trainer_data,
                        party_data=party_data,
                        delete_mode=s.delete_mode,
                        action=action
                    )
                )
                y_offset += 190 # Odstęp między slotami
            except Exception as e:
                print(f"Failed to load save {folder}: {e}")

    def select_save(s, path):
        s.game.state_manager.add_state("Singleplayer", Singleplayer(s.game, path))
        s.game.state_manager.change_state("Singleplayer")

    def delete_save(s, path):
        try:
            shutil.rmtree(path)
            s.load_saves()
        except Exception as e:
            print(f"Error deleting save: {e}")

    def new_save(s):
        s.game.state_manager.change_state("New save wizzard")

    def handling_events(s, events):
        ctrl = s.game.controlls_data
        mouse_pos = s.game.get_scaled_mouse_pos()

        for event in events:

            if event.type == pygame.KEYDOWN:

                # ---------- SAVE LOGS ----------
                if s.active_index_menu == "saves":

                    if event.key == ctrl['up']:
                        if s.active_index > 0:
                            s.active_index -= 1
                        else:
                            # przejście do UI
                            s.active_index_menu = "ui"
                            s.active_index = 0

                        s.game.audio_manager.play_sound(s.game.select_sound)

                    elif event.key == ctrl['down']:
                        if s.active_index < len(s.save_buttons) - 1:
                            s.active_index += 1

                        s.game.audio_manager.play_sound(s.game.select_sound)

                    elif event.key == ctrl['action_a']:
                        if s.save_buttons:
                            s.save_buttons[s.active_index].press()

                # ---------- UI BUTTONS ----------
                elif s.active_index_menu == "ui":

                    if event.key == ctrl['left']:
                        s.active_index = (s.active_index - 1) % len(s.menu_buttons)
                        s.game.audio_manager.play_sound(s.game.select_sound)

                    elif event.key == ctrl['right']:
                        s.active_index = (s.active_index + 1) % len(s.menu_buttons)
                        s.game.audio_manager.play_sound(s.game.select_sound)

                    elif event.key == ctrl['down']:
                        if s.save_buttons:
                            s.active_index_menu = "saves"
                            s.active_index = 0
                            s.game.audio_manager.play_sound(s.game.select_sound)

                    elif event.key == ctrl['action_a']:
                        b = s.menu_buttons[s.active_index]

                        if hasattr(b, "press"):
                            b.press()
                        else:
                            b.action()

                if event.key == ctrl['action_b']:
                    s.menu_buttons[0].press()
                

        # ---------- MOUSE HOVER ----------
        for i, b in enumerate(s.menu_buttons):
            if b.rect.collidepoint(mouse_pos):
                s.active_index_menu = "ui"
                s.active_index = i

        for i, b in enumerate(s.save_buttons):
            if b.rect.collidepoint(mouse_pos):
                s.active_index_menu = "saves"
                s.active_index = i

        # ---------- SELECTED STATE ----------
        for i, b in enumerate(s.menu_buttons):
            if hasattr(b, "is_selected"):
                b.is_selected = s.active_index_menu == "ui" and i == s.active_index

        for i, b in enumerate(s.save_buttons):
            b.is_selected = s.active_index_menu == "saves" and i == s.active_index

        # ---------- EVENT PASS ----------
        for b in s.menu_buttons + s.save_buttons:
            b.handling_events(events)

    def update(s, delta_time):
        s.bg_color = s.bg_color.lerp(s.target_bg_color, 0.1)

        for i, b in enumerate(s.menu_buttons):
            if hasattr(b, "is_selected"):
                b.is_selected = s.active_index_menu == "ui" and i == s.active_index
            b.update(delta_time)

        for i, b in enumerate(s.save_buttons):
            b.is_selected = s.active_index_menu == "saves" and i == s.active_index
            b.update(delta_time)

    def draw(s, window):
        window.fill(s.bg_color)
        
        # Tytuł menu
        title_font = pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 60)
        title_text = "SELECT EXPEDITION" if not s.delete_mode else "REMOVE EXPEDITION"
        title_color = (255, 255, 255) if not s.delete_mode else (255, 100, 100)
        title_surf = title_font.render(title_text, True, title_color)
        window.blit(title_surf, (300, 50))

        for b in s.menu_buttons + s.save_buttons:
            b.draw(window)

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

        s.width = int(WINDOW_WIDTH * 0.85)
        s.height = 160
        s.rect = pygame.Rect(0, 0, s.width, s.height)
        s.rect.center = pos

        s.hover = False
        s.is_selected = False
        s.y_offset = 0 # Do animacji najechania
        
        # Dane do wyświetlenia
        s.name = manifest.get("slot_name", "Empty Slot")
        s.badges = manifest.get("badges", 0)
        s.location = world_data.get("current_map", "Unknown Area").replace("_", " ").title()
        s.gender = trainer_data.get("gender", "male")

    def get_trainer_icon(s):
        try:
            key = "player_male" if s.gender == "male" else "player_female"
            return s.game.overworld_frames["characters"][key]['down'][0]
        except:
            surf = pygame.Surface((64, 64))
            surf.fill((100,100,100))
            return surf

    def press(s):
        s.game.audio_manager.play_sound(s.game.select_sound)
        s.action()

    def get_monster_icon(s, monster_name):
        return s.game.monster_icons.get(monster_name, pygame.Surface((40, 40), pygame.SRCALPHA))

    def handling_events(s, events):
        mouse_pos = s.game.get_scaled_mouse_pos()
        s.hover = s.rect.collidepoint(mouse_pos)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and s.hover:
                s.game.audio_manager.play_sound(s.game.select_sound)
                s.action()

    def update(s, delta_time):
        mouse_pos = s.game.get_scaled_mouse_pos()
        s.hover = s.rect.collidepoint(mouse_pos)
        
        # Animacja "pływania" przy najechaniu (Lerp)
        target_y = -8 if s.hover else 0
        s.y_offset += (target_y - s.y_offset) * 0.15

    def draw(s, window):
        # Rysujemy z uwzględnieniem animowanego offsetu
        draw_rect = s.rect.copy()
        draw_rect.y += s.y_offset

        # 1. Cień
        shadow_rect = draw_rect.copy()
        shadow_rect.y += 8
        pygame.draw.rect(window, (10, 10, 15, 80), shadow_rect, border_radius=15)

        # 2. Tło slotu
        selected = s.hover or s.is_selected

        if s.delete_mode:
            bg_color = (180,45,45) if not selected else (220,60,60)
            border_color = (255,100,100)
        else:
            bg_color = (45,50,85) if not selected else (60,70,130)
            border_color = (100,110,200) if selected else (70,75,110)

        pygame.draw.rect(window, bg_color, draw_rect, border_radius=15)
        pygame.draw.rect(window, border_color, draw_rect, width=3, border_radius=15)

        # 3. Ikona trenera
        t_icon = pygame.transform.scale_by(s.get_trainer_icon(), 1.5)
        window.blit(t_icon, (draw_rect.x + 30, draw_rect.centery - t_icon.get_height() // 2))

        # 4. Teksty
        fonts = s.game.save_file_log_fonts
        name_surf = fonts['big'].render(s.name, True, (255, 255, 255))
        info_surf = fonts['small'].render(f"Badges: {s.badges} | {s.location}", True, (200, 200, 230))
        
        window.blit(name_surf, (draw_rect.x + 250, draw_rect.y + 40))
        window.blit(info_surf, (draw_rect.x + 250, draw_rect.y + 90))

        # 5. Party Icons (po prawej)
        s.draw_party(window, draw_rect)

    def draw_party(s, window, draw_rect):
        start_x = draw_rect.right - 600
        y = draw_rect.centery
        
        for i, monster in enumerate(s.party_data.get("slots", [])[:5]):
            pos = (start_x + (i * 130), y)
            pygame.draw.circle(window, (20, 20, 40, 100), pos, 28)
            
            if monster:
                icon = s.get_monster_icon(monster.get("name"))
                # Lekkie bujanie ikonek
                bob = math.sin(pygame.time.get_ticks() * 0.005 + i) * 3
                rect = icon.get_rect(center=(pos[0], pos[1] + bob))
                window.blit(icon, rect)
            else:
                pygame.draw.circle(window, (255, 255, 255, 30), pos, 10, width=1)