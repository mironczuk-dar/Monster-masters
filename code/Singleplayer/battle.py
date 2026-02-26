#IMPORTING LIBRAIES
import pygame
from random import choice

#IMPORTING FILES
from Singleplayer.singleplayer_settings import *
from Singleplayer.battle_sprites import MonsterSprite, MonsterNameSprite, MonsterLevelSprite, MonsterStatsSprite, MonsterOutlineSprite, AttackSprite, TimedSprite
from Singleplayer.battle_camera import BattleSprites
from UI_elements.bar import draw_bar
from Tools.timer import Timer
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

#IMPORTING DATA 
from Manifest.abilities_manifest import ABILITIES_DATA
from Manifest.elements_manifest import ELEMENT_RELATIONS

class Battle:
    def __init__(s, game, singleplayer_state, players_monsters, opponents_monsters, bg_surface, fonts, battle_type = 'single'):

        #GAME ATTRIBUTES
        s.game = game
        s.singleplayer_state = singleplayer_state

        #MONSTERS
        s.players_monsters = players_monsters
        s.opponents_monsters = opponents_monsters

        #VISUAL ATTRIBUTES
        s.fonts = fonts
        s.bg_surface = bg_surface

        #MONSTER DATA
        s.monster_data = {'player' : players_monsters, 'opponent' : opponents_monsters}

        #BATTLE TYPE ATTRIBUTES
        s.battle_type = battle_type
        s.battle_limits = {'single': 1, 'doubles': 2, 'triples': 3}
        s.max_monsters = s.battle_limits.get(s.battle_type, 1)

        #GROUPS
        s.battle_sprites = BattleSprites(s.game)
        s.player_sprites = pygame.sprite.Group()
        s.opponent_sprites = pygame.sprite.Group()

        #CONTROLLING MONSTER
        s.current_monster = None
        s.selection_mode = None
        s.selection_side = 'player'
        s.selected_attack = None
        s.indexes = {
            'general' : 0,
            'monster' : 0,
            'attacks' : 0,
            'switch' : 0,
            'target' : 0
        }

        #UNIWERSAL CATCH RATE
        s.catch_rate = 1

        #BATTLE RESULTS
        s.finished = False
        s.result = None  # 'win' / 'lose'

        #TIMERS
        s.timers = {
            'opponent delay' : Timer(600, False, s.opponent_attack)
        }

        #SETTING UP THE BATTLE
        s.setup()

    #BATTLE SYSTEM METHODS
    def check_active(s):
        for montser_sprite in s.player_sprites.sprites() + s.opponent_sprites.sprites():
            if montser_sprite.monster.initiative >= 100:
                montser_sprite.monster.defending = False
                s.update_all_monsters('pause')
                montser_sprite.monster.initiative = 0
                montser_sprite.set_highlight(True)
                s.current_monster = montser_sprite
                if s.player_sprites in montser_sprite.groups():
                    s.selection_mode = 'general'
                else:
                    s.timers['opponent delay'].activate()

    def update_all_monsters(s, option):
        for montser_sprites in s.player_sprites.sprites() + s.opponent_sprites.sprites():
            montser_sprites.monster.paused = True if option == 'pause' else False

    def opponent_attack(s):
        ability = choice(s.current_monster.monster.get_abilities())
        
        random_target = choice(s.opponent_sprites.sprites()) if ABILITIES_DATA[ability]['target'] == 'player' else choice(s.player_sprites.sprites())

        s.current_monster.activate_attack(random_target, ability)

    def check_end_of_battle(s):
        player_alive = any(m is not None and m.health > 0 for m in s.players_monsters.values())

        opponent_alive = any(m is not None and m.health > 0 for m in s.opponents_monsters.values())
        if not opponent_alive:
            opponent_alive = any(ms.monster.health > 0 for ms in s.opponent_sprites)

        if not player_alive:
            s.finished = True
            s.result = 'lose'
            return

        if not opponent_alive:
            for monster in s.players_monsters.values():
                if monster is not None:
                    monster.initiative = 0
            s.finished = True
            s.result = 'win'
            return

    #UI METHODS
    def draw_ui(s, window):
        if s.current_monster:
            if s.selection_mode == 'general':
                s.draw_general_options(window)
            if s.selection_mode == 'attacks':
                s.draw_attacks(window)
            if s.selection_mode == 'switch':
                s.draw_switch(window)

    def draw_general_options(s, window):
        for index, (option, data_dict) in enumerate(BATTLE_CHOICES['full'].items()):
            if index == s.indexes['general']:
                surface = s.game.battle_icons_outline[data_dict['icon']]
            else:
                surface = pygame.transform.scale_by(s.game.battle_icons[data_dict['icon']], 0.6)
            rect = surface.get_frect(center = s.current_monster.rect.midright + data_dict['pos'])
            window.blit(surface, rect)

    def draw_attacks(s, window):

        #DATA
        abilities = s.current_monster.monster.get_abilities(all = False)
        height = 300
        width = 200
        visible_attacks = 4
        item_height = height / visible_attacks
        v_offset = 0 if s.indexes['attacks'] < visible_attacks else -(s.indexes['attacks'] - visible_attacks + 1) * item_height

        #BACKGROUND
        bg_rect = pygame.FRect((0,0), (width, height)).move_to(midleft = s.current_monster.rect.midright + vector(20,0))
        pygame.draw.rect(window, COLORS['white'], bg_rect, 0, 5)

        for index, ability in enumerate(abilities):
            selected = index == s.indexes['attacks']

            if selected:
                element = ABILITIES_DATA[ability]['element']
                text_colour = COLORS[element] if element != 'normal' else COLORS['black']

            else:
                text_colour = COLORS['light']
            text_surface = s.fonts['regular'].render(ability, False, text_colour)
            text_rect = text_surface.get_frect(center = bg_rect.midtop + vector(0, item_height / 2+index*item_height+v_offset))
            text_bg_rect = pygame.FRect((0,0), (width, item_height)).move_to(center = text_rect.center)

            if bg_rect.collidepoint(text_rect.center):
                if selected:
                    if text_bg_rect.collidepoint(bg_rect.topleft):
                        pygame.draw.rect(window, COLORS['dark white'], text_bg_rect, 0,0,10,10)
                    elif text_bg_rect.collidepoint(bg_rect.midbottom + vector(0,-1)):
                        pygame.draw.rect(window, COLORS['dark white'], text_bg_rect, 0,0,0,0, 10, 10)
                    else:
                        pygame.draw.rect(window, COLORS['dark white'], text_bg_rect)
                window.blit(text_surface, text_rect)

    def draw_switch(s, window):
        width = 450
        height = 460
        visible_monsters = 4
        item_height = height / visible_monsters
        v_offset = 0 if s.indexes['switch'] < visible_monsters else -(s.indexes['switch'] - visible_monsters + 1) * item_height
        bg_rect = pygame.FRect((0,0), (width, height)).move_to(midleft = s.current_monster.rect.midright + vector(20, 0))

        pygame.draw.rect(window, COLORS['white'], bg_rect, 0, 5)

        #AVAILABLE MONSTERS
        active_monster = [(monster_sprite.index, monster_sprite.monster) for monster_sprite in s.player_sprites]
        s.available_monsters = {
                index: monster for index, monster in s.monster_data['player'].items() 
                if monster is not None and (index, monster) not in active_monster and monster.health > 0
            }

        for index, monster in enumerate(s.available_monsters.values()):
            selected = index == s.indexes['switch']
            item_bg_rect = pygame.FRect((0,0), (width, item_height)).move_to(midleft = (bg_rect.left, bg_rect.top + item_height/2 + index * item_height + v_offset))
            icon_surface = s.game.monster_icons[monster.name]
            icon_rect = icon_surface.get_frect(midleft = bg_rect.topleft + vector(10, item_height/2 + index * item_height + v_offset))
            text_surface = s.fonts['regular'].render(f'{monster.name} - Lvl: {monster.level}', False, COLORS['red'] if selected else COLORS['black'])
            text_rect = text_surface.get_frect(topleft = (bg_rect.left + 135, icon_rect.top))

            if selected:
                if item_bg_rect.collidepoint(bg_rect.topleft):
                    pygame.draw.rect(window, COLORS['dark white'], item_bg_rect, 0, 0, 5, 5)
                elif item_bg_rect.collidepoint(bg_rect.midbottom + vector(0,-1)):
                    pygame.draw.rect(window, COLORS['dark white'], item_bg_rect, 0,0,0,0, 5, 5)
                else:
                    pygame.draw.rect(window, COLORS['dark white'], item_bg_rect)

            if bg_rect.collidepoint(item_bg_rect.center):
                for surface, rect in ((icon_surface, icon_rect), (text_surface, text_rect)):
                    window.blit(surface, rect)
                health_rect = pygame.FRect(text_rect.bottomleft + vector(0, 10), (300, 8))
                energy_rect = pygame.FRect(health_rect.bottomleft + vector(0, 8), (300, 8))
                draw_bar(window, health_rect, monster.health, monster.get_stat('max_health'), COLORS['green'], COLORS['black'])
                draw_bar(window, energy_rect, monster.energy, monster.get_stat('max_energy'), COLORS['blue'], COLORS['black'])

    def apply_attack(s, target_sprite, attack, damage_ammount):
        animation_name = ABILITIES_DATA[attack]['animation']
        frames = s.game.attack_frames[animation_name]
        AttackSprite(s.battle_sprites, target_sprite.rect.center, frames)

        attack_element = ABILITIES_DATA[attack]['element']
        target_element = target_sprite.monster.element


        multiplier = ELEMENT_RELATIONS.get(attack_element, {}).get(target_element, 1.0)
        final_damage = damage_ammount * multiplier

        if animation_name != 'green':
            target_defence = 1 - target_sprite.monster.get_stat('defense') / 1000
            if target_sprite.monster.defending:
                target_defence -= 0.2
            target_defence = max(0, min(1, target_defence))


            target_sprite.monster.health -= damage_ammount * target_defence
        else:
            target_sprite.monster.health -= damage_ammount

        s.update_all_monsters('resume')

    def check_death(s):
        for monster_sprite in s.opponent_sprites.sprites() + s.player_sprites.sprites():
            if monster_sprite.monster.health <= 0 and not monster_sprite.timers['kill'].active:

                new_monster_data = None

                if s.player_sprites in monster_sprite.groups():
                    active_monsters_objs = [ms.monster for ms in s.player_sprites.sprites() if ms.monster.health > 0]
                    
                    available_monsters = [
                        (index, monster) for index, monster in s.monster_data['player'].items() 
                        if monster is not None and monster.health > 0 and monster not in active_monsters_objs
                    ]
                    
                    if available_monsters:
                        new_idx, new_monster_obj = available_monsters[0]
                        new_monster_data = (new_monster_obj, monster_sprite.index, 'player')

                else:
                    available_opponents = [
                        (idx, m) for idx, m in s.opponents_monsters.items() 
                        if m is not None and m.health > 0 and m not in [os.monster for os in s.opponent_sprites]
                    ]
                    
                    if available_opponents:
                        new_idx, new_monster_obj = available_opponents[0]
                        new_monster_data = (new_monster_obj, monster_sprite.index, 'opponent')

                monster_sprite.delayed_kill(new_monster_data)

    #GENERAL METHODS
    def setup(s):
        for entity, monsters in s.monster_data.items():
            for index, monster in monsters.items():
                # DODANY WARUNEK: monster.health > 0
                if index < s.max_monsters and monster is not None and monster.health > 0:
                    s.create_monster(monster, index, entity)

            for i in range(len(s.opponent_sprites)):
                if i in s.opponents_monsters:
                    del s.opponents_monsters[i]

    def create_monster(s, monster, index, entity, pos = None):
        frames = s.game.monster_assets[monster.name]
        outline_frames = s.game.monster_outlines[monster.name]
        
        if pos == None:
            positions = BATTLE_POSITIONS[s.battle_type][entity]
            pos_index = index if index < len(positions) else 0
            pos = positions[pos_index]

        groups = [s.battle_sprites]
        if entity == 'player':
            groups.append(s.player_sprites)
            frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in frames.items()}
            outline_frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in outline_frames.items()}
        else:
            groups.append(s.opponent_sprites)

        monster_sprite = MonsterSprite(groups, pos, frames, monster, index, entity, s.apply_attack, s.create_monster)
        MonsterOutlineSprite(monster_sprite, s.battle_sprites, outline_frames)

        monster.paused = False

        #UI ELEMENTS
        name_pos = monster_sprite.rect.midleft + vector(0, -70) if entity == 'player' else monster_sprite.rect.midright + vector(0, -70)
        name_sprite = MonsterNameSprite(s.battle_sprites, name_pos, monster_sprite, s.fonts['regular'])
        level_pos = name_sprite.rect.bottomleft if entity =='player' else name_sprite.rect.bottomright
        MonsterLevelSprite(s.battle_sprites, entity, level_pos, monster_sprite, s.fonts['small'])
        MonsterStatsSprite(s.battle_sprites, monster_sprite.rect.midbottom + vector(0,30), monster_sprite, (225, 90), s.fonts['stats'])

    def update(s, delta_time):

        if s.finished:
            return

        s.check_end_of_battle()

        s.battle_sprites.update(delta_time)

        s.check_active()
        s.check_death()

        for timer in s.timers.values():
            timer.update()

    def draw(s, window):
        window.blit(s.bg_surface, (0,0))
        
        s.battle_sprites.draw(window, s.current_monster, s.selection_side, s.selection_mode, s.indexes['target'], s.player_sprites, s.opponent_sprites)
        s.draw_ui(window)

    def handling_events(s, events):
        controlls = s.game.controlls_data

        if (
            s.selection_mode 
            and s.current_monster 
            and s.current_monster in s.player_sprites
        ):
            keys = pygame.key.get_just_pressed()

            # 1. Dynamiczne ustalanie limitera
            limiter = 0
            if s.selection_mode == 'general':
                limiter = len(BATTLE_CHOICES['full'])
            elif s.selection_mode == 'attacks':
                limiter = len(s.current_monster.monster.get_abilities(all=False))
            elif s.selection_mode == 'switch':
                # Pobieramy aktualne potwory w walce
                active_indices = [ms.index for ms in s.player_sprites]
                s.available_monsters = {
                    index: monster for index, monster in s.monster_data['player'].items() 
                    if monster is not None and index not in active_indices and monster.health > 0
                }
                limiter = len(s.available_monsters)
            elif s.selection_mode == 'target':
                sprite_group = s.opponent_sprites if s.selection_side == 'opponent' else s.player_sprites
                limiter = len(sprite_group.sprites())

            # 2. Nawigacja góra/dół
            if limiter > 0:
                if keys[controlls['up']]:
                    s.indexes[s.selection_mode] = (s.indexes[s.selection_mode] - 1) % limiter
                if keys[controlls['down']]:
                    s.indexes[s.selection_mode] = (s.indexes[s.selection_mode] + 1) % limiter
            else:
                s.indexes[s.selection_mode] = 0

            # 3. Potwierdzenie (Action A)
            if keys[controlls['action_a']]:
                
                if s.selection_mode == 'target':
                    sprite_group = s.opponent_sprites if s.selection_side == 'opponent' else s.player_sprites
                    sprites_list = sprite_group.sprites()
                    if sprites_list:
                        target_sprite = sprites_list[s.indexes['target']]

                        if s.selected_attack:
                            s.current_monster.activate_attack(target_sprite, s.selected_attack)
                            s.selected_attack = None
                            s.current_monster = None
                            s.selection_mode = None
                        else:
                            max_h = target_sprite.monster.get_stat('max_health')
                            current_h = target_sprite.monster.health
                            actual_player_monster_count = len([m for m in s.monster_data['player'].values() if m is not None])
                            
                            if current_h < max_h * s.catch_rate:
                                if actual_player_monster_count < 5:
                                    for i in range(5):
                                        if s.monster_data['player'].get(i) is None:
                                            s.monster_data['player'][i] = target_sprite.monster
                                            break
                                    
                                    target_sprite.delayed_kill(None)
                                    info_surface = s.fonts['regular'].render("Monster has been captured!", False, COLORS['green'])
                                    TimedSprite(s.battle_sprites, (WINDOW_WIDTH/2, WINDOW_HEIGHT - info_surface.height - 5), info_surface, 1000)
                                    
                                    s.update_all_monsters('resume')
                                else:
                                    info_surface = s.fonts['regular'].render("Your party is full!", False, COLORS['red'])
                                    TimedSprite(s.battle_sprites, (WINDOW_WIDTH/2, WINDOW_HEIGHT - info_surface.height - 5), info_surface, 1000)
                                    TimedSprite(s.battle_sprites, target_sprite.rect.center, s.game.battle_icons['cross'], 1000)
                            else:
                                info_surface = s.fonts['regular'].render("Monster health too high for capture!", False, COLORS['red'])
                                TimedSprite(s.battle_sprites, (WINDOW_WIDTH/2, WINDOW_HEIGHT - info_surface.height - 5), info_surface, 1000)
                                TimedSprite(s.battle_sprites, target_sprite.rect.center, s.game.battle_icons['cross'], 1000)
                        
                elif s.selection_mode == 'attacks':
                    abilities = s.current_monster.monster.get_abilities(all=False)

                    if not abilities:
                        # ... (Twój kod obsługi braku umiejętności)
                        return

                    # 1. NAPRAWA: Pobierz i zapisz wybraną umiejętność do s.selected_attack
                    s.indexes['attacks'] %= len(abilities)
                    s.selected_attack = abilities[s.indexes['attacks']] # To było pominięte!

                    # 2. Teraz s.selected_attack nie jest już None, więc to zadziała:
                    s.selection_side = ABILITIES_DATA[s.selected_attack]['target']
                    
                    sprite_group = s.opponent_sprites if s.selection_side == 'opponent' else s.player_sprites
                    sprites_list = sprite_group.sprites()

                    if len(sprites_list) == 1:
                        target_sprite = sprites_list[0]
                        # Używamy s.selected_attack, które już ma wartość
                        s.current_monster.activate_attack(target_sprite, s.selected_attack)
                        
                        s.selected_attack = None
                        s.current_monster.set_highlight(False)
                        s.update_all_monsters('resume')
                        s.current_monster = None
                        s.selection_mode = None
                    else:
                        s.selection_mode = 'target'
                        s.indexes['target'] = 0

                elif s.selection_mode == 'general':
                    if s.indexes['general'] == 0: # Fight
                        s.selection_mode = 'attacks'
                        s.indexes['attacks'] = 0

                    elif s.indexes['general'] == 1: # Defend / Wait
                        s.current_monster.defending = True
                        s.update_all_monsters('resume')
                        s.current_monster.set_highlight(False)
                        s.current_monster = None
                        s.selection_mode = None

                    elif s.indexes['general'] == 2: # Switch
                        s.selection_mode = 'switch'
                        s.indexes['switch'] = 0

                    elif s.indexes['general'] == 3: # Catch
                        s.selection_mode = 'target'
                        s.selection_side = 'opponent'

                elif s.selection_mode == 'switch':
                    print(s.available_monsters)
                    index, new_monster = list(s.available_monsters.items())[s.indexes['switch']]
                    s.current_monster.kill()
                    old_pos = s.current_monster.pos
                    s.create_monster(new_monster, index, 'player', old_pos)
                    s.update_all_monsters('resume')
                    s.selection_mode = None
                    


                s.indexes = {k:0 for k in s.indexes}

            # 4. Powrót (Action B)
            if keys[controlls['action_b']]:
                if s.selection_mode in ('attacks', 'switch', 'target'):
                    s.selection_mode = 'general'
                    s.selection_side = None
                    s.selected_attack = None
                    s.indexes['target'] = 0