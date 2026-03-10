#IMPORTING LIBRAIRIES
import pygame
from random import sample

#IMPORTING FILES
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from States.generic_state import BaseState

#IMPORTING TOOLS
from UI_elements.keyboard import Keyboard
from Tools.asset_scaling_tools import outline_creator, scale_asset

#IMPORTING DATA
from Manifest.monster_manifest import *

class NewSaveWizard(BaseState):

    def __init__(s, game):
        super().__init__(game)

        s.trainer_name = ""
        s.gender = None
        s.starter = None

        s.steps = []
        s.step_index = 0
        s.current_step = None

    def on_enter(s):

        s.steps = [
            NameStep(s),
            GenderStep(s),
            StarterStep(s)
        ]

        s.step_index = 0
        s.current_step = s.steps[0]
        s.current_step.on_enter()

    def next_step(s):

        s.step_index += 1

        if s.step_index >= len(s.steps):
            s.finish()
            return

        s.current_step = s.steps[s.step_index]
        s.current_step.on_enter()

    def finish(s):

        save_folder = s.create_save_files(
            s.trainer_name,
            s.gender,
            s.starter
        )

        s.game.state_manager.change_state("Singleplayer menu")

    def handling_events(s, events):
        s.current_step.handling_events(events)

    def update(s, delta_time):
        s.current_step.update(delta_time)

    def draw(s, window):

        s.current_step.draw(window)

        steps = ["Name", "Gender", "Starter"]

        font = pygame.font.SysFont("Arial", 22)

        for i, step in enumerate(steps):

            color = (255,255,0) if i == s.step_index else (150,150,150)

            txt = font.render(step, True, color)

            x = WINDOW_WIDTH//2 + (i-1)*200
            window.blit(txt, txt.get_rect(center=(x,40)))

    def create_save_files(s, name, gender, starter):
        from os.path import join
        from os import makedirs
        import json
        from settings import BASE_DIR

        from Manifest.save_file_manifest import (
            DEFAULT_SAVE_FILE_MANIFEST,
            DEFAULT_TRAINER,
            DEFAULT_PARTY,
            DEFAULT_PC,
            DEFAULT_WORLD,
            DEFAULT_FLAGS,
            DEFAULT_INVENTORY
        )

        saves_dir = join(BASE_DIR, "data", "saves")

        save_folder = join(
            saves_dir,
            f"Save_{name}_{pygame.time.get_ticks()}"
        )

        makedirs(save_folder, exist_ok=True)

        # --- MANIFEST ---
        manifest = DEFAULT_SAVE_FILE_MANIFEST.copy()
        manifest["slot_name"] = name

        # --- TRAINER ---
        trainer = DEFAULT_TRAINER.copy()
        trainer["name"] = name
        trainer["gender"] = gender

        # --- PARTY ---
        party = {
            "slots": [
                None, None, None, None, None
            ]
        }

        starter_level = 5
        if starter is not None:
            starter_stats = MONSTER_DATA[starter]['stats']
            party["slots"][0] = {
                "name": starter,
                "level": starter_level,
                "exp": 0,
                "health": starter_stats['max_health'] * starter_level,
                "energy": starter_stats['max_energy'] * starter_level
            }

        files_to_create = {
            "manifest.json": manifest,
            "trainer.json": trainer,
            "party.json": party,
            "pc.json": DEFAULT_PC,
            "world.json": DEFAULT_WORLD,
            "flags.json": DEFAULT_FLAGS,
            "inventory.json": DEFAULT_INVENTORY
        }

        for filename, data in files_to_create.items():

            path = join(save_folder, filename)

            with open(path, "w") as f:
                json.dump(data, f, indent=4)

        return save_folder

class WizardStep:

    def __init__(s, wizard):
        s.wizard = wizard
        s.game = wizard.game

    def on_enter(s):
        pass

    def handling_events(s, events):
        pass

    def update(s, dt):
        pass

    def draw(s, window):
        pass

class NameStep(WizardStep):

    def on_enter(s):

        keyboard_pos = (100, 400)

        s.keyboard = Keyboard(
            s.game,
            pos=keyboard_pos,
            size=(WINDOW_WIDTH - 2 * keyboard_pos[0], WINDOW_HEIGHT - keyboard_pos[1] - 100),
            max_length=12
        )

        s.title_font = pygame.font.SysFont("Arial", 42)
        s.preview_font = pygame.font.SysFont("Arial", 48)
        s.info_font = pygame.font.SysFont("Arial", 24)

    def handling_events(s, events):
        s.keyboard.handling_events(events)


    def update(s, dt):

        s.wizard.trainer_name = s.keyboard.text

        if s.keyboard.finished and s.keyboard.text:
            s.keyboard.finished = False
            s.wizard.next_step()

    def draw(s, window):

        window.fill((30,30,50))

        # --- TITLE ---
        txt = s.title_font.render("Enter Your Name", True, (255,255,255))
        rect = txt.get_rect(center=(WINDOW_WIDTH//2,120))
        window.blit(txt, rect)

        # --- NAME PREVIEW ---
        max_len = s.keyboard.max_length
        name = s.keyboard.text

        display_name = name + "-" * (max_len - len(name))

        preview = s.preview_font.render(display_name, True, (255,255,0))
        preview_rect = preview.get_rect(center=(WINDOW_WIDTH//2,200))
        window.blit(preview, preview_rect)

        # --- REMAINING CHARACTERS ---
        remaining = max_len - len(name)

        info = s.info_font.render(
            f"{remaining} characters remaining",
            True,
            (200,200,200)
        )

        info_rect = info.get_rect(center=(WINDOW_WIDTH//2,250))
        window.blit(info, info_rect)

        # --- KEYBOARD ---
        s.keyboard.draw(window)

class GenderStep(WizardStep):

    def __init__(s, wizard):
        super().__init__(wizard)

        s.male_player_frames = s.game.overworld_frames['characters']['player_male']
        s.female_player_frames = s.game.overworld_frames['characters']['player_female']

        s.male_player_frames = scale_asset(s.male_player_frames, 3)
        s.female_player_frames = scale_asset(s.female_player_frames, 3)

        s.character_sprite_directions = ['down', 'left', 'up', 'right']

        s.options = ["male", "female"]

        # animation
        s.frame_index = 0
        s.frame_speed = 0.15

        # rotation animation
        s.character_sprite_direction_index = 0
        s.direction_timer = 0
        s.direction_interval = 600

    def on_enter(s):
        s.index = 0

        s.frame_index = 0
        s.character_sprite_direction_index = 0
        s.direction_timer = pygame.time.get_ticks()

    def handling_events(s, events):

        ctrl = s.game.controlls_data

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == ctrl["left"]:
                    s.index = (s.index - 1) % len(s.options)

                if event.key == ctrl["right"]:
                    s.index = (s.index + 1) % len(s.options)

                if event.key == ctrl["action_a"]:
                    s.select()

    def update(s, delta_time):

        # idle animation
        s.frame_index += s.frame_speed * delta_time

        # rotate character
        now = pygame.time.get_ticks()

        if now - s.direction_timer > s.direction_interval:
            s.direction_timer = now
            s.character_sprite_direction_index = (s.character_sprite_direction_index + 1) % 4

    def draw(s, window):

        window.fill((30,30,50))

        font = pygame.font.SysFont("Arial", 42)

        title = font.render("Select Gender", True, (255,255,255))
        window.blit(title, title.get_rect(center=(WINDOW_WIDTH//2,150)))

        # character
        s.draw_character(window)

        for i, g in enumerate(s.options):

            color = (255,255,0) if i == s.index else (200,200,200)

            txt = font.render(g.capitalize(), True, color)

            x = WINDOW_WIDTH//2 + (i-0.5)*200

            window.blit(txt, txt.get_rect(center=(x,720)))

    
    def draw_character(s, window):
        direction = s.character_sprite_directions[s.character_sprite_direction_index]

        if s.options[s.index] == "male":
            frames = s.male_player_frames[direction]
        else:
            frames = s.female_player_frames[direction]

        frame = frames[0]

        rect = frame.get_rect(center=(WINDOW_WIDTH//2, 400))

        window.blit(frame, rect)

    def select(s):
        s.wizard.gender = s.options[s.index]
        s.wizard.next_step()

class StarterStep(WizardStep):

    def on_enter(s):
        # 1. Selection of starters
        all_starters = STARTER_LIST
        s.starters = sample(all_starters, 3)
        s.index = 0

        # 2. Empty lists for processed frames
        s.frames = []      # Will be a list of lists: [[frames_mon1], [frames_mon2], [frames_mon3]]
        s.outlines = []    # Will be a list of lists: [[outlines_mon1], [outlines_mon2], [outlines_mon3]]

        # 3. Processing selected monsters
        for name in s.starters:
            # Get base frames
            raw_idle_frames = s.game.monster_assets[name]["idle"]
            
            # Dynamic scaling
            scale = 1.8
            
            scaled_frames = []
            monster_outlines = []

            for f in raw_idle_frames:
                # Scale the individual frame
                scaled_f = pygame.transform.scale(
                    f, (int(f.get_width() * scale), int(f.get_height() * scale))
                )
                scaled_frames.append(scaled_f)
                
                # Create the outline for this specific frame
                # We wrap it in a dict because outline_creator expects one
                temp_dict = {"temp": scaled_f}
                temp_outlines_dict = outline_creator(temp_dict, 8)
                
                # Extract the resulting surface and add to our list
                monster_outlines.append(temp_outlines_dict["temp"])

            # Append the full animation sets to the state lists
            s.frames.append(scaled_frames)
            s.outlines.append(monster_outlines)

        # 4. Animation logic
        s.frame_index = [0] * len(s.starters) 
        s.frame_timer = 0
        s.frame_speed = 0.2 

        # 5. Fonts
        s.title_font = pygame.font.SysFont("Arial", 42, bold=True)
        s.name_font = pygame.font.SysFont("Arial", 36)

    def handling_events(s, events):
        ctrl = s.game.controlls_data
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == ctrl["left"]:
                    s.index = (s.index - 1) % len(s.starters)
                elif event.key == ctrl["right"]:
                    s.index = (s.index + 1) % len(s.starters)
                elif event.key == ctrl["action_a"]:
                    s.select()

    def select(s):
        # Przypisujemy wybranego potwora do kreatora/czarodzieja
        s.wizard.starter = s.starters[s.index]
        s.wizard.next_step()

    def update(s, dt):
        s.frame_timer += dt
        if s.frame_timer >= s.frame_speed:
            s.frame_timer = 0
            for i in range(len(s.starters)):
                # Bezpieczne zapętlanie animacji dla każdego potwora z osobna
                s.frame_index[i] = (s.frame_index[i] + 1) % len(s.frames[i])

    def draw(s, window):
        window.fill((30, 30, 50)) # Ciemne tło

        # TYTUŁ
        title = s.title_font.render("Select Your Starter", True, (255, 255, 255))
        window.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))

        spacing = 550 # Dostosuj do szerokości okna
        for i, name in enumerate(s.starters):
            # Środek dla każdego potwora
            x = WINDOW_WIDTH // 2 + (i - 1) * spacing
            y = WINDOW_HEIGHT // 2

            # Pobieramy konkretną klatkę animacji
            current_idx = s.frame_index[i]
            sprite = s.frames[i][current_idx]
            
            # 1. Rysujemy OUTLINE (tylko dla wybranego)
            if i == s.index:
                outline = s.outlines[i][current_idx]
                rect_out = outline.get_rect(center=(x, y))
                window.blit(outline, rect_out)

            # 2. Rysujemy SPRITE (zawsze)
            rect_spr = sprite.get_rect(center=(x, y))
            window.blit(sprite, rect_spr)

            # 3. Rysujemy NAZWĘ
            is_selected = (i == s.index)
            color = (255, 255, 0) if is_selected else (200, 200, 200)
            
            # Mały efekt "pływania" nazwy dla wybranego potwora (opcjonalnie)
            offset_y = 10 if is_selected else 0 
            txt = s.name_font.render(name.capitalize(), True, color)
            window.blit(txt, txt.get_rect(center=(x, y + 200 + offset_y)))