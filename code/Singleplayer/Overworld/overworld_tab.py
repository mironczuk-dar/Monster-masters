import pygame

# IMPORTING FILES
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from Singleplayer.singleplayer_settings import COLORS
from Singleplayer.Overworld.overworld_sprites import TimedSprite

class OverworldTab:
    def __init__(s, game, singleplayer):
        s.game = game
        s.singleplayer_state = singleplayer

        # SIZE ATTRIBUTES
        s.width = WINDOW_WIDTH * 0.3
        s.height = WINDOW_HEIGHT

        # INITIALIZING SURFACE
        s.image = pygame.Surface((s.width, s.height), pygame.SRCALPHA)
        s.rect = s.image.get_rect(topright=(WINDOW_WIDTH, 0))

        # OPTIONS FOR THE MENU
        s.options = ["Monster-Dex", "Party", "Backpack", "Trainer ID", "Options", "Save", "Exit"]
        s.index = 0
        
        # UI SETTINGS
        s.padding = 20
        s.button_height = (s.height - (s.padding * 2)) / len(s.options)
        
        # SPRITE GROUP FOR UI NOTIFICATIONS (TimedSprites)
        s.ui_sprites = pygame.sprite.Group()
        
        s.setup()

    def setup(s):
        s.image.fill((0, 0, 0, 180)) 
        pygame.draw.rect(s.image, COLORS['white'], (0, 0, s.width, s.height), 4)

    def draw(s, window):
        # 1. Draw the base menu background
        window.blit(s.image, s.rect)
        
        # 2. Draw dynamic buttons
        for i, option in enumerate(s.options):
            bg_color = COLORS['grey'] if i == s.index else COLORS['light-grey']
            text_color = COLORS['white'] if i == s.index else COLORS['black']
            
            rect_x = s.rect.x + s.padding
            rect_y = s.padding + (i * s.button_height)
            button_rect = pygame.Rect(rect_x, rect_y, s.width - (s.padding * 2), s.button_height - 10)
            
            pygame.draw.rect(window, bg_color, button_rect, border_radius=5)
            if i == s.index:
                pygame.draw.rect(window, COLORS['white'], button_rect, 2, border_radius=5)
            
            font = s.game.overworld_tab_fonts['medium']
            text_surf = font.render(option, True, text_color)
            text_rect = text_surf.get_rect(center=button_rect.center)
            window.blit(text_surf, text_rect)

        # 3. Draw TimedSprites (Notifications like "Saved!")
        s.ui_sprites.draw(window)

    def update(s, delta_time):
        # Updates timers and kills sprites when their time is up
        s.ui_sprites.update(delta_time)

    def handling_events(s, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                controlls = s.game.controlls_data
                
                if event.key == controlls['up']:
                    s.index = (s.index - 1) % len(s.options)
                elif event.key == controlls['down']:
                    s.index = (s.index + 1) % len(s.options)
                elif event.key == controlls['action_a']: 
                    s.select_option()
                elif event.key == controlls['options'] or event.key == controlls['action_b']:
                    s.game.audio_manager.play_sound(s.game.overworld_tab_sounds['close'])
                    s.singleplayer_state.overworld_tab_active = False

    def select_option(s):
        option = s.options[s.index]
        
        if option == "Monster-Dex":
            print('Opening monster-dex...')
            
        elif option == "Party":
            s.singleplayer_state.monster_party_active = True
            s.singleplayer_state.overworld_tab_active = False

        elif option == "Options":
            s.game.state_manager.change_state("Options menu")
            
        elif option == "Save":
            s.singleplayer_state.save()
            info_surface = s.game.overworld_tab_fonts['big'].render("Game Saved!", True, COLORS['red'])
            
            TimedSprite(
                s.ui_sprites, 
                (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50), 
                info_surface, 
                1500
            )

        elif option == "Exit":
            s.singleplayer_state.save()
            s.game.state_manager.change_state("Start menu")

    def on_enter(s):
        s.index = 0
        s.ui_sprites.empty() # Clear old notifications when re-opening menu