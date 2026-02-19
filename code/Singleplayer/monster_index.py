#IMPORTING LIBRARIES
import pygame

#IMPORITNG FILES
from Singleplayer.singleplayer_settings import *
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

#IMPORTING DATA
from Manifest.monster_manifest import MONSTER_DATA
from Manifest.abilities_manifest import ABILITIES_DATA

#UI ELEMENTS
from UI_elements.bar import draw_bar

class MonsterIndex:
    def __init__(s, game, singleplayer_state, monsters, fonts):

        s.game = game
        s.singleplayer_state = singleplayer_state

        #MONSTER INDEX ATTRIBUTES
        s.monsters = monsters
        s.visible_items = 5
        s.index = 0
        s.selected_index = None
        s.frame_index = 0
        
        #MAXIMUM STATS A MONSTER CAN HAVE
        s.max_stats = {}
        for data in MONSTER_DATA.values():
            for stat, value in data['stats'].items():
                if stat != 'element':
                    if stat not in s.max_stats:
                        s.max_stats[stat] = value
                    else:
                        s.max_stats[stat] = max(s.max_stats[stat], value)

        if 'max_health' in s.max_stats:
            s.max_stats['health'] = s.max_stats.pop('max_health')
        if 'max_energy' in s.max_stats:
            s.max_stats['energy'] = s.max_stats.pop('max_energy')

        #TINT SIRFACE
        s.tint_furface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        s.tint_furface.set_alpha(200)

        #DIMENTIONS
        s.main_rect = pygame.FRect(0,0, WINDOW_WIDTH*0.6, WINDOW_HEIGHT*0.9).move_to(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        s.list_width = s.main_rect.width * 0.3
        s.item_height = s.main_rect.height / s.visible_items

        #FONTS
        s.fonts = fonts


    def update(s, delta_time):
        s.frame_index += ANIMATION_SPEED * delta_time

    def draw(s, window):
        window.blit(s.tint_furface, (0,0))

        s.display_list(window)
        s.display_main(window)

    def handling_events(s, events):
        controlls = s.game.controlls_data
        key = pygame.key.get_just_pressed()

        active_monsters_count = len([m for m in s.monsters.values() if m is not None])

        if key[controlls['options']]:
            s.singleplayer_state.monster_index_active = False

        if key[controlls['action_a']]:
            if s.selected_index != None:
                selected_monster = s.monsters[s.selected_index]
                current_monster = s.monsters[s.index]

                s.monsters[s.index] = selected_monster
                s.monsters[s.selected_index] = current_monster
                s.selected_index = None
            else:
                s.selected_index = s.index

        if active_monsters_count > 0:
            if key[controlls['up']]:
                s.index -= 1
            if key[controlls['down']]:
                s.index += 1

            s.index = s.index % active_monsters_count

    def on_enter(s):
        pass

    def display_main(s, window):

        #DATA
        monster = s.monsters[s.index]

        rect = pygame.FRect(s.main_rect.left + s.list_width, s.main_rect.top, s.main_rect.width - s.list_width, s.main_rect.height)
        pygame.draw.rect(window, COLORS['dark'], rect, 0, 50, 0, 50, 0)

        #MONSTER DISPLAY
        top_rect = pygame.FRect(rect.left, rect.top, rect.width, rect.height * 0.4)
        pygame.draw.rect(window, COLORS[monster.element], top_rect, 0,0,0, 50)

        #MONSTER NAME
        name_surface = s.fonts['bold'].render(monster.name, False, COLORS['white'])
        name_rect = name_surface.get_frect(topleft = top_rect.topleft + vector(10,10))
        window.blit(name_surface, name_rect)

        #MONSTER LEVEL
        level_surface = s.fonts['regular'].render(f'Lvl: {monster.level}', False, COLORS['white'])
        level_rect = level_surface.get_frect(bottomleft = top_rect.bottomleft + vector(10,-10))
        window.blit(level_surface, level_rect)

        #MONSTER ELEMENT
        element_surface = s.fonts['regular'].render(f'Type: {monster.element}', False, COLORS['white'])
        element_rect = element_surface.get_frect(bottomright = top_rect.bottomright + vector(-10,-10))
        window.blit(element_surface, element_rect)

        #EXP BAR
        draw_bar(window,
                pygame.FRect(level_rect.bottomleft, (200,6)),
                monster.exp,
                monster.level_up,
                COLORS['blue'],
                COLORS['dark'])

        #MONSTER ANIMATION
        monster_surface = s.game.monster_assets[monster.name]['idle'][int(s.frame_index % len(s.game.monster_assets[monster.name]['idle']))]
        monster_rect = monster_surface.get_frect(center = top_rect.center)
        window.blit(monster_surface, monster_rect)

        #HEALTH AND ENERGY BAR
        bar_data = {
            'width' : rect.width * 0.45,
            'height' : 50,
            'top' : top_rect.bottom + rect.width * 0.03,
            'left_side' : rect.left + rect.width / 4,
            'right_side' : rect.left + rect.width * 3/4
        }

        health_bar_rect = pygame.FRect((0,0), (bar_data['width'], bar_data['height'])).move_to(midtop = (bar_data['left_side'], bar_data['top']))
        draw_bar(window, health_bar_rect, monster.health, monster.get_stat('max_health'), (0,180,0), COLORS['red'], 10)
        hp_text = s.fonts['small'].render(f'HP: {int(monster.health)} / {int(monster.get_stat("max_health"))}', False, COLORS['white'])
        hp_text_rect = hp_text.get_frect(midleft = health_bar_rect.midleft + vector(10,0))
        window.blit(hp_text, hp_text_rect)

        energy_bar_rect = pygame.FRect((0,0), (bar_data['width'], bar_data['height'])).move_to(midtop = (bar_data['right_side'], bar_data['top']))
        draw_bar(window, energy_bar_rect, monster.energy, monster.get_stat('max_energy'), (0,0,255), COLORS['light-grey'], 10)
        energy_text = s.fonts['small'].render(f'ENG: {int(monster.energy)} / {int(monster.get_stat("max_energy"))}', False, COLORS['white'])
        energy_text_rect = energy_text.get_frect(midleft = energy_bar_rect.midleft + vector(10,0))
        window.blit(energy_text, energy_text_rect)

        #POSITIONING ATTRIBUES
        sides = {'left' : health_bar_rect.left, 'right' : energy_bar_rect.left}
        info_height = rect.bottom - health_bar_rect.bottom

        #STAT TEXT
        stats_rect = pygame.FRect(sides['left'], health_bar_rect.bottom, health_bar_rect.width, info_height).inflate(0,-120).move(0, 30)
        stats_text_surface = s.fonts['regular'].render('Stats', False, COLORS['white'])
        stats_text_rect = stats_text_surface.get_frect(midbottom = stats_rect.midtop)
        window.blit(stats_text_surface, stats_text_rect)

        monster_stats = monster.get_stats()
        stat_height = stats_rect.height / len(monster_stats)
        for index, (stat, value) in enumerate(monster_stats.items()):
            single_stat_rect = pygame.FRect(stats_rect.left, stats_rect.top + index * stat_height, stats_rect.width, stat_height)

            #STAT ICONS
            icon_surface = s.game.stat_icons[stat.lower()]
            icon_rect = icon_surface.get_frect(midleft = single_stat_rect.midleft + vector(10,0))
            window.blit(icon_surface, icon_rect)

            #STATS TEXT
            text_surface = s.fonts['small'].render(stat, False, COLORS['white'])
            text_rect = text_surface.get_frect(topleft = icon_rect.topleft + vector(50, -10))
            window.blit(text_surface, text_rect)

            #STAT BARS
            bar_rect = pygame.FRect((text_rect.left, text_rect.bottom + 2), (single_stat_rect.width - (text_rect.left - single_stat_rect.left), 6))
            draw_bar(window, bar_rect, value, s.max_stats[stat.lower()] * monster.level, COLORS['white'], COLORS['black'])


        #MONSTER ATTACKS
        abilities_rect = stats_rect.copy().move_to(left = sides['right'])
        abilities_text_surface = s.fonts['regular'].render('Abilities', False, COLORS['white'])
        abilities_text_rect = abilities_text_surface.get_frect(midbottom = abilities_rect.midtop)
        window.blit(abilities_text_surface, abilities_text_rect)

        for index, ability in enumerate(monster.get_abilities()):
            element = ABILITIES_DATA[ability]['element']

            text_surface = s.fonts['small'].render(ability, False, COLORS['black'])
            x = abilities_rect.left + 50
            y = 40 + abilities_rect.top + index * (text_surface.height + 30)
            rect = text_surface.get_frect(topleft = (x,y))
            pygame.draw.rect(window, COLORS[element], rect.inflate(10,10), 0, 10)
            window.blit(text_surface, rect)


    def display_list(s, window):
        bg_rect = pygame.FRect(s.main_rect.topleft, (s.list_width, s.main_rect.height))
        pygame.draw.rect(window, COLORS['grey'], bg_rect, 0, 0,50, 0, 50)

        v_offset = 0 if s.index < s.visible_items else -(s.index - s.visible_items + 1) * s.item_height

        for index, monster in s.monsters.items():
            if monster is not None: 
                bg_colour = COLORS['grey'] if s.index != index else COLORS['light']
                text_colour = COLORS['white'] if s.selected_index != index else COLORS['gold']

                top = s.main_rect.top + index * s.item_height + v_offset
                item_rect = pygame.FRect(s.main_rect.left, top, s.list_width, s.item_height)

                if item_rect.colliderect(s.main_rect):
                    if item_rect.collidepoint(s.main_rect.topleft):
                        pygame.draw.rect(window, bg_colour, item_rect, 0, 0, 50)
                    elif item_rect.collidepoint(s.main_rect.bottomleft + vector(1, -1)):
                        pygame.draw.rect(window, bg_colour, item_rect, 0, 0, 0, 0, 50)
                    else:
                        pygame.draw.rect(window, bg_colour, item_rect)

                    text_surface = s.fonts['regular'].render(monster.name, False, text_colour)
                    text_rect = text_surface.get_frect(midleft = (item_rect.midleft) + vector(130, 0))
                    icon_surface = s.game.monster_icons[monster.name]
                    icon_rect = icon_surface.get_frect(center = item_rect.midleft + vector(60, 0))

                    window.blit(text_surface, text_rect)
                    window.blit(icon_surface, icon_rect)

        active_monsters = [m for m in s.monsters.values() if m is not None]
        for i in range(len(active_monsters)):
            if i != 0:
                y = s.main_rect.top + i * s.item_height + v_offset
            
                if s.main_rect.top <= y <= s.main_rect.bottom:
                    pygame.draw.line(
                        window, 
                        COLORS['light-grey'], 
                        (s.main_rect.left, y), 
                        (s.main_rect.left + s.list_width, y), 
                        6
                    )
                
        last_line_y = s.main_rect.top + len(active_monsters) * s.item_height + v_offset
        if s.main_rect.top < last_line_y <= s.main_rect.bottom:
            pygame.draw.line(window, COLORS['light-grey'], (s.main_rect.left, last_line_y), (s.main_rect.left + s.list_width, last_line_y), 2)

        shadow_surface = pygame.Surface((6, s.main_rect.height))
        window.blit(shadow_surface, (s.main_rect.left + s.list_width - 4, s.main_rect.top))
                