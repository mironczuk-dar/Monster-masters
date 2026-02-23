from pygame.math import Vector2 as vector

TILE_SIZE = 64 
ANIMATION_SPEED = 6
BATTLE_OUTLINE_WIDTH = 4

COLORS = {
	'white': '#f4fefa', 
	'pure white': '#ffffff',
	'dark': '#2b292c',
	'light': '#c8c8c8',
	'grey': '#3a373b',
	'gold': '#ffd700',
	'light-grey': '#4b484d',
	'fire':'#f8a060',
	'water':'#50b0d8',
	'plant': '#64a990', 
	'black': '#000000', 
	'red': '#f03131',
	'blue': '#66d7ee',
	'normal': '#ffffff',
	'dark white': '#f0f0f0',
    'green' : (0, 180, 0)
}

WORLD_LAYERS = {
	'water': 0,
	'terrain': 1,
	'shadow': 2,
	'main': 3,
	'top': 4
}

BATTLE_POSITIONS = {
    'single': {
        'player': [(305, 600)],
        'opponent': [(1630, 585)]
    },
    'doubles': {
        'player': [(305, 600), (655, 780)],
        'opponent': [(1630, 585), (1275, 800)]
    },
    'triples': {
        'player': [(305, 600), (685, 780), (570, 390)],
        'opponent': [(1630, 585), (1255, 800), (1330, 390)]
    }
}

BATTLE_LAYERS =  {
	'outline': 0,
	'name': 1,
	'monster': 2,
	'effects': 3,
	'overlay': 4
}

BATTLE_CHOICES = {
    'full': {
        'fight':  {'pos' : vector(45, -90), 'icon': 'sword'},
        'defend': {'pos' : vector(60, -30), 'icon': 'shield'},
        'switch': {'pos' : vector(60, 30), 'icon': 'arrows'},
        'catch':  {'pos' : vector(45, 90), 'icon': 'hand'}},
    
    'limited': {
        'fight':  {'pos' : vector(45, -60), 'icon': 'sword'},
        'defend': {'pos' : vector(60, 0), 'icon': 'shield'},
        'switch': {'pos' : vector(45, 60), 'icon': 'arrows'}}
}