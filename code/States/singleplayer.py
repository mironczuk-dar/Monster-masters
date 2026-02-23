#IMPORTING FILES
from pygame.math import Vector2 as vector

#IMPORTING FILES
from settings import *
from States.generic_state import BaseState
from Singleplayer.world import World
from Singleplayer.monster_index import MonsterIndex
from Singleplayer.battle import Battle

#IMPORTING DATA
from Tools.data_loading_tools import load_data, save_data
from Manifest.save_file_manifest import *
from Singleplayer.monsters import Monster


class Singleplayer(BaseState):
    def __init__(s, game, save_path):
        s.game = game

        #PLAYERS SAVE FILE
        s.save_path = save_path
        s.loading_in_save_file_data()

        #SINGLEPLAYER GAME ELEMENTS
        s.world = World(s.game, s)

        #SINGLEPLAYER GAME FLAGS
        s.monster_index_active = False
        s.currently_in_battle = True

        #SETTING UP SINGLEPLAYER GAME ELEMENTS
        s.tint_setup()
        s.setup()

        #MONSTER INDEX - MONSTERDEX
        s.monster_index = MonsterIndex(s.game, s, s.player_party, s.game.monster_index_fonts)

        #BATTLE SYSTEM ATTRIBUTES
        s.dummy_monsters = {
            0: Monster("Sparchu", 5, 0, 120, 70),
            1: Monster("Friolera", 2, 0, 300, 490),
            2: Monster("Friolera", 2, 0, 180, 65),
            3: Monster("Friolera", 2, 0, 250, 100),
            4: None
        }
        s.battle = Battle(s.game, s, s.player_party, s.dummy_monsters, game.bg_frames['forest'], game.battle_fonts, 'triples')

    def save(s):
        from os.path import join
        
        if hasattr(s.world, 'player'):
            s.save_data['world_data']['position']['x'] = s.world.player.rect.centerx
            s.save_data['world_data']['position']['y'] = s.world.player.rect.centery
            s.save_data['world_data']['current_map'] = s.world.current_map_name
            s.save_data['world_data']['position']['facing_direction'] = s.world.player.facing_direction

        # Przykład dla ekwipunku/flag (jeśli world je przechowuje):
        # s.save_data['inventory_data'] = s.world.inventory.get_data()
        # s.save_data['flags_data'] = s.world.flags

        s.update_party_data()

        # 2. ZAPISYWANIE DO PLIKÓW
        for key, data in s.save_data.items():
            # key to np. 'trainer_data', musimy odciąć '_data' żeby dostać nazwę pliku
            file_name = f"{key.replace('_data', '')}.json"
            full_path = join(s.save_path, file_name)
            save_data(data, full_path)
            
        print(f"Game saved successfully in {s.save_path}")

    def update_party_data(s):
        updated_slots = [None] * 5

        for i, monster_obj in s.player_party.items():
            if monster_obj is not None:
                if 0 <= i < 5:
                    updated_slots[i] = {
                        'name': monster_obj.name,
                        'level': monster_obj.level,
                        'exp': monster_obj.exp,
                        'health': monster_obj.health,
                        'energy': monster_obj.energy
                    }
            else:
                updated_slots[i] = None

        s.save_data['party_data']['slots'] = updated_slots

    def loading_in_save_file_data(s):
        from os.path import join

        s.save_data = {
        'trainer_data' : load_data(join(s.save_path, "trainer.json"), DEFAULT_TRAINER),
        'world_data' : load_data(join(s.save_path, "world.json"), DEFAULT_WORLD),
        'party_data' : load_data(join(s.save_path, "party.json"), DEFAULT_PARTY),
        'pc_data' : load_data(join(s.save_path, "pc.json"), DEFAULT_PC),
        'flags_data' : load_data(join(s.save_path, "flags.json"), DEFAULT_FLAGS),
        'inventory_data' : load_data(join(s.save_path, "inventory.json"), DEFAULT_INVENTORY)
        }

        s.load_player_monsters()

    def load_player_monsters(s):
        s.player_party = {}

        for i, monster_data in enumerate(s.save_data['party_data']['slots']):
            if monster_data:
                name = monster_data['name']
                level = monster_data['level']
                exp = monster_data['exp']
                health = monster_data['health']
                energy = monster_data['energy']
                
                s.player_party[i] = Monster(name, level, exp, health, energy)
            else:
                s.player_party[i] = None
        
    def setup(s):

        #SETTING UP THE MAP
        s.world.setup()

        #CONVERTING MONSTER DATA IN TO MONSTER DATA OBJECTS
        s.load_player_monsters()

    def update(s, delta_time):

        if s.monster_index_active:
            s.monster_index.update(delta_time)
            return

        if s.currently_in_battle:
            s.battle.update(delta_time)
            return

        if s.world.portal_destination and s.tint_mode == 'idle':
            s.tint_mode = 'tint'

        s.tint_window(delta_time)

        if s.tint_mode == 'idle':
            s.world.update(delta_time)

    def draw(s, window):
        window.fill((50, 50, 50))

        if s.monster_index_active:
            s.monster_index.draw(window)
        elif s.currently_in_battle:
            s.battle.draw(window)
        else:
           s.world.draw(window)

        window.blit(s.tint_surface, s.tint_rect)

    def handling_events(s, events):

        if s.monster_index_active:
            s.monster_index.handling_events(events)
            s.world.player.direction = vector(0,0)

        elif s.currently_in_battle:
            s.battle.handling_events(events)

        else:
            s.world.handling_events(events)

    def tint_window(s, delta_time):
        speed = s.tint_speed * delta_time

        if s.tint_mode == 'tint':
            s.tint_rect.y += speed
            if s.tint_rect.top >= 0:
                s.tint_rect.top = 0
                s.tint_mode = 'load'

        elif s.tint_mode == 'load':
            if s.world.portal_destination:
                s.world.setup(map_name=s.world.portal_destination)
                s.world.portal_destination = None
            s.tint_mode = 'untint'

        elif s.tint_mode == 'untint':
            s.tint_rect.y -= speed
            if s.tint_rect.top <= -WINDOW_HEIGHT:
                s.tint_rect.top = -WINDOW_HEIGHT
                s.tint_mode = 'idle'

    def tint_setup(s):
        s.tint_surface = s.game.tint_surface
        s.tint_surface.fill((0,0,0))
        s.tint_rect = s.tint_surface.get_frect(topleft=(0, -WINDOW_HEIGHT))
        s.tint_mode = 'untint'
        s.tint_speed = 1800