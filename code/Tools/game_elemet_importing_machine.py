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
        'Options menu tune' : join(BASE_DIR, 'audio', 'Music_tracs', 'Options_menu_tune.ogg'),
    }

    game.options_menu_sound = pygame.mixer.Sound(join(BASE_DIR, 'audio', 'Sound effects', 'scratch.mp3'))


#LOADING GAME MAPS
def load_maps(game):

    game.maps = {
        'house' : load_pygame(join(BASE_DIR, 'data', 'maps', 'house.tmx')),
        'world' : load_pygame(join(BASE_DIR, 'data', 'maps', 'world.tmx')),
        'hospital' : load_pygame(join(BASE_DIR, 'data', 'maps', 'hospital.tmx')),
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
    game.tint_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    game.monster_icons = import_folder_dict(BASE_DIR, 'assets', 'icons')
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



#LOADING GAME FONTS
def load_game_fonts(game):

    game.overworld_fonts = {
        'dialog' : pygame.font.Font(join(BASE_DIR, 'assets', 'fonts', 'PixeloidSans.ttf'), 40)
    }

    game.monster_index_fonts = {
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