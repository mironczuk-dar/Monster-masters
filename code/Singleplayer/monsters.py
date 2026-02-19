#IMPORTING FILES
from Manifest.monster_manifest import *

class Monster:
    def __init__(s, name, level, exp, health, energy):

        s.name = name
        s.level = level

        #MONSTER STATS
        s.base_stats = MONSTER_DATA[s.name]['stats']
        s.element = s.base_stats['element']

        #MONSTER ABILITIES
        s.abilities = MONSTER_DATA[s.name]['abilities']

        #MONSTER LEVEL AND EXP
        s.exp = exp
        s.level_up = s.level * 150

        #MONSTER HEALTH AND ENERGY
        s.health = health
        s.energy = energy

    def get_stat(s, stat):
        return s.base_stats[stat] * s.level
    
    def get_stats(s):
        return {
            'Health' : s.get_stat('max_health'),
            'Energy' : s.get_stat('max_energy'),
            'Attack' : s.get_stat('attack'),
            'Defense' : s.get_stat('defense'),
            'Speed' : s.get_stat('speed'),
            'Recovery' : s.get_stat('recovery'),
        }
    
    def get_abilities(s):
        return [ability for lvl, ability in s.abilities.items() if s.level >= lvl]