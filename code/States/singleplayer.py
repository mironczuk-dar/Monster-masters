#IMPORTING FILES
from pygame.math import Vector2 as vector
from random import choice

#IMPORTING FILES
from settings import *
from States.generic_state import BaseState
from Singleplayer.world import World
from Singleplayer.monster_index import MonsterIndex
from Singleplayer.battle import Battle
from Singleplayer.death_screen import DeathScreen
from Singleplayer.non_player_characters import NonPlayerCharacter

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
        s.death_screen = None

        #SINGLEPLAYER GAME FLAGS
        s.monster_index_active = False
        s.currently_in_battle = False
        s.pending_death_screen = False

        #SETTING UP SINGLEPLAYER GAME ELEMENTS
        s.tint_setup()
        s.setup()

        #MONSTER INDEX - MONSTERDEX
        s.monster_index = MonsterIndex(s.game, s, s.player_party, s.game.monster_index_fonts)

        #BATTLE SYSTEM ATTRIBUTES
        s.dummy_monsters = {
            0: Monster("Sparchu", 15, 0, 120, 70),
            1: Monster("Friolera", 12, 0, 120, 490),
            2: Monster("Friolera", 12, 0, 120, 65),
            3: Monster("Friolera", 2, 0, 120, 100),
            4: None
        }
        s.battle = None

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
            
            if s.battle.finished and s.tint_mode == 'idle':
                s.tint_mode = 'tint' 
            
        
        if s.world.portal_destination and s.tint_mode == 'idle':
            s.tint_mode = 'tint'

        s.tint_window(delta_time)

        if s.tint_mode == 'idle' and not s.currently_in_battle and not s.monster_index_active:
            s.world.update(delta_time)

    def draw(s, window):
        window.fill((50, 50, 50))

        if s.monster_index_active:
            s.monster_index.draw(window)
        elif s.currently_in_battle:
            s.battle.draw(window)
        elif s.death_screen:
            s.death_screen.draw(window)
        else:
           s.world.draw(window)

        window.blit(s.tint_surface, s.tint_rect)

    def handling_events(s, events):

        if s.monster_index_active:
            s.monster_index.handling_events(events)
            s.world.player.direction = vector(0,0)

        elif s.currently_in_battle:
            s.battle.handling_events(events)

        elif s.death_screen:
            s.death_screen.handling_events(events)

        else:
            s.world.handling_events(events)

    def create_battle(s, character_id):
        from Manifest.npc_manifest import CHARACTER_DATA
        from Singleplayer.monsters import OpponentMonster
        
        npc_data = CHARACTER_DATA.get(character_id)
        if not npc_data: return

        opponent_monsters = {}
        for slot, data in npc_data['monsters'].items():
            if data:
                name, level = data
                opponent_monsters[slot] = OpponentMonster(name, level)
            else:
                opponent_monsters[slot] = None

        s.pending_battle_data = {
            'opponents': opponent_monsters,
            'bg': npc_data.get('biome', 'forest'),
            'character_id': character_id
        }

        s.tint_mode = 'tint'

    def nurse_heal(s):
        for monster in s.player_party.values():
            if monster is not None:
                monster.health = monster.get_stat('max_health')
                monster.energy = monster.get_stat('max_energy')
        print("Party healed!")
        s.world.player.freeze_unfreeze()

    def tint_window(s, delta_time):
        speed = s.tint_speed * delta_time

        if s.tint_mode == 'tint':
            s.tint_rect.y += speed
            if s.tint_rect.top >= 0:
                s.tint_rect.top = 0
                s.tint_mode = 'load'

        elif s.tint_mode == 'load':
            if s.currently_in_battle and s.battle.finished:
                if s.battle.result == 'lose':
                    s.death_screen = DeathScreen(s.game, s, choice(s.game.death_screens), s.save_path)
                
                if s.battle.result == 'win' and hasattr(s, 'active_battle_char_id'):
                    char_id = s.active_battle_char_id
                    
                    if char_id not in s.save_data['flags_data']['characters_defeated']:
                        s.save_data['flags_data']['characters_defeated'].append(char_id)
                    
                    from Manifest.npc_manifest import CHARACTER_DATA
                    for npc in s.world.all_sprite_groups['characters']:
                        if isinstance(npc, NonPlayerCharacter) and npc.character_id == char_id:
                            npc.defeated = True
                            
                            s.world.create_dialog(npc)
                            break

                s.currently_in_battle = False
                s.world.player.freeze_unfreeze()
                
                
            elif hasattr(s, 'pending_battle_data') and s.pending_battle_data:
                data = s.pending_battle_data
                s.active_battle_char_id = data['character_id']
                
                s.battle = Battle(
                    s.game, s, s.player_party, 
                    data['opponents'], 
                    s.game.bg_frames[data['bg']], 
                    s.game.battle_fonts, 'triples'
                )
                
                s.currently_in_battle = True
                s.pending_battle_data = None

            elif s.world.portal_destination:
                s.world.setup(map_name=s.world.portal_destination)
                s.world.portal_destination = None
                
            s.tint_mode = 'untint'
                
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

    def delete_save_file(s):
        import shutil
        import os

        if not os.path.isdir(s.save_path):
            print("Invalid save path.")
            return

        # Bezpiecznik
        if "saves" not in s.save_path.lower():
            print("Unsafe path. Abort.")
            return

        try:
            shutil.rmtree(s.save_path)
            print(f"Deleted: {s.save_path}")
        except Exception as e:
            print(f"Error deleting save: {e}")
            return

        s.game.state_manager.change_state("Start menu")