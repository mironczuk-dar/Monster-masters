#IMPORTING LIBRARIES
from pygame import mixer
from pytmx.util_pygame import load_pygame

#IMPORTING FILES
from Tools.asset_importing_tool import *
from Tools.asset_scaling_tools import scale_asset, outline_creator
from settings import BASE_DIR
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


#LOADING IN AUDIO FILES
def load_audio_assets(game):

    #INITIALIZING MIXER
    mixer.init()

    game.music_tracks = {
        'Start menu tune' : join(BASE_DIR, 'audio', 'Music_tracs', 'States_tunes', 'start_menu_tune.ogg'),
        'Singleplayer menu tune' : join(BASE_DIR, 'audio', 'Music_tracs', 'States_tunes', 'singleplayer_menu_tune.ogg'),
        'Options menu tune' : join(BASE_DIR, 'audio', 'Music_tracs', 'States_tunes', 'options_menu_tune.ogg'),
        'World map tune' : join(BASE_DIR, 'audio', 'Music_tracs', 'Overworld_tunes', 'world_map_tune.ogg'),
        'Hospital tune' : join(BASE_DIR, 'audio', 'Music_tracs', 'Overworld_tunes', 'hospital_tune.ogg'),
        'Default battle tune' : join(BASE_DIR, 'audio', 'Music_tracs', 'Battle_tunes', 'default_battle_tune.ogg'),
        'Its going down now' : join(BASE_DIR, 'audio', 'Music_tracs', 'Battle_tunes', 'its_going_down_now.ogg'),
    }

    game.select_sound = pygame.mixer.Sound(join(BASE_DIR, 'audio', 'Sound_effects', 'generic_sounds', 'select_sound.wav'))
    game.transition_screen_sound = pygame.mixer.Sound(join(BASE_DIR, 'audio', 'Sound_effects', 'overworld_sounds', 'transition_screen_sound.wav'))
    game.start_menu_monster_cries = {
        'Pluma' : pygame.mixer.Sound(join(BASE_DIR, 'audio', 'Sound_effects', 'start_menu_sounds','pluma_cry.wav')),
        'Friolera' : pygame.mixer.Sound(join(BASE_DIR, 'audio', 'Sound_effects', 'start_menu_sounds','friolera_cry.wav')),
        'Finiette' : pygame.mixer.Sound(join(BASE_DIR, 'audio', 'Sound_effects', 'start_menu_sounds','finiette_cry.wav')),
    }
    game.hospital_heal_sound = pygame.mixer.Sound(join(BASE_DIR, 'audio', 'Sound_effects', 'overworld_sounds', 'hospital_heal_sound.wav'))

    game.overworld_tab_sounds = {
        'open' : pygame.mixer.Sound(join(BASE_DIR, 'audio', 'Sound_effects', 'overworld_tab_sounds', 'overworld_tab_open.wav')),
        'close' : pygame.mixer.Sound(join(BASE_DIR, 'audio', 'Sound_effects', 'overworld_tab_sounds', 'overworld_tab_close.wav')),
    }

#LOADING GAME MAPS
def load_maps(game):

    game.maps = {
        'house' : load_pygame(join(BASE_DIR, 'data', 'maps', 'house.tmx')),
        'world' : load_pygame(join(BASE_DIR, 'data', 'maps', 'world.tmx')),
        'hospital' : load_pygame(join(BASE_DIR, 'data', 'maps', 'hospital.tmx')),
        'Stag Island' : load_pygame(join(BASE_DIR, 'data', 'maps', 'stag_island.tmx')),
    }

#LOADING LEVEL ASSETS
def load_assets(game):
    SCALE_FACTOR = WINDOW_WIDTH / WINDOW_HEIGHT

    game.overworld_frames = {
        'water' : import_folder(BASE_DIR, 'assets', 'tilesets', 'water'),
        'coast' : coast_importer( 24, 12, BASE_DIR, 'assets', 'tilesets', 'coast'),
        'characters' : all_character_import(BASE_DIR, 'assets', 'characters'),
        'shadow' : import_image(BASE_DIR, 'assets', 'other', 'shadow'),
        'notice_mark' : import_image(BASE_DIR, 'assets', 'ui', 'notice')
    }
    game.transition_surface = import_image(BASE_DIR, 'assets', 'transition_screens', 'transition_screen_1')
    game.transition_surface = pygame.transform.scale(game.transition_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))

    game.monster_icons = import_folder_dict(BASE_DIR, 'assets', 'monster_icons')
    game.monster_icons = scale_asset(game.monster_icons, SCALE_FACTOR)

    game.monster_assets = monster_asset_importer(4, 2, BASE_DIR, 'assets', 'monsters')

    game.monster_assets = scale_asset(game.monster_assets, SCALE_FACTOR)
    game.monster_outlines = outline_creator(game.monster_assets, 8)

    game.stat_icons = import_folder_dict(BASE_DIR, 'assets', 'ui')
    game.battle_icons = scale_asset(game.stat_icons, SCALE_FACTOR)
    game.battle_icons_outline = outline_creator(game.battle_icons, 6)
    game.stat_icons = scale_asset(game.stat_icons, 2)

    game.attack_frames = attack_importer(BASE_DIR, 'assets', 'attacks')

    game.bg_frames = import_folder_dict(BASE_DIR, 'assets', 'backgrounds')
    game.bg_frames = scale_asset(game.bg_frames, SCALE_FACTOR)

    game.death_screens = import_folder(BASE_DIR, 'assets', 'death_screens')
    game.death_screens = [pygame.transform.scale(surface, (WINDOW_WIDTH, WINDOW_HEIGHT)) for surface in game.death_screens]

#LOADING GAME FONTS
def load_game_fonts(game):

    game.overworld_fonts = {
        'dialog' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 40)
    }

    game.overworld_tab_fonts = {
        'medium' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 30),
        'big' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 50)
    }

    game.monster_party_fonts = {
        'regular' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 33),
        'small' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 29),
        'bold' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'dogicapixelbold.otf'), 39),
    }

    game.battle_fonts = {
        'regular' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 33),
        'small' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 25),
        'bold' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'dogicapixelbold.otf'), 39),
        'stats' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 20),
    }

    game.save_file_log_fonts = {
        'big' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 42),
        'medium' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 32),
        'small' :   pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 28)
    }