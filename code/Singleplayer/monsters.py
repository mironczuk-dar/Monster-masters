#IMPORTING FILES
from Manifest.monster_manifest import *

#IMPORINT DATA
from Manifest.abilities_manifest import ABILITIES_DATA

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

        #BATTLE READYNESS/INITATIVE | WHO ATTACKS FIRST 
        s.initiative = 0
        s.paused = False
        

    def __repr__(s):
        return f'monster : {s.name}, lvl: {s.level}'

    def get_stat(s, stat):
        return s.base_stats[stat] * s.level
    
    def reduce_energy(s, attack):
        s.energy -= ABILITIES_DATA[attack]['cost']

    def get_base_damage(s, attack):
        return s.get_stat('attack') * ABILITIES_DATA[attack]['amount']
    
    def get_stats(s):
        return {
            'Health' : s.get_stat('max_health'),
            'Energy' : s.get_stat('max_energy'),
            'Attack' : s.get_stat('attack'),
            'Defense' : s.get_stat('defense'),
            'Speed' : s.get_stat('speed'),
            'Recovery' : s.get_stat('recovery'),
        }
    
    def get_abilities(s, all = True):
        if all:
            return [ability for lvl, ability in s.abilities.items() if s.level >= lvl]
        else:
            return [ability for lvl, ability in s.abilities.items() if s.level >= lvl and ABILITIES_DATA[ability]['cost'] < s.energy]

    def get_info(s):
        return (
            (s.health, s.get_stat('max_health')),
            (s.energy, s.get_stat('max_energy')),
            (s.initiative, 100)
        )
    
    def update(s, delta_time):
        s.update_initative(delta_time)
    
    def update_initative(s, delta_time):
        if not s.paused:
            s.initiative += s.get_stat('speed') * delta_time