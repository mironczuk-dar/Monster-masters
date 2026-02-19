#IMPROTING FILES
from settings import *
from settings import AUDIO_DATA_PATH
from Tools.data_loading_tools import save_data
from UI_elements.pop_ups import MusicPopUp
from pygame import mixer
from Tools.timer import Timer

#AUDIO MANAGER CLASS
class AudioManager:

    # CONSTRUCTOR
    def __init__(s, game):
        s.game = game

        # ----- MUSIC -----
        s.state_music = {
            'Start menu' : 'Options menu tune',
            'Options menu' : 'Options menu tune',
            'Singleplayer menu' : 'Options menu tune',
        }

        # ----- MUSIC EFFECTS -----
        s.current_track = None
        s.music_on = s.game.audio_data.get('music_on', True)
        s.music_volume = s.game.audio_data.get('music_volume', 1.0)

        # ----- SOUND EFFECTS -----
        s.sound_on = s.game.audio_data.get('sound_on', True)
        s.sound_volume = s.game.audio_data.get('sound_volume', 1.0)

        # ----- SOUND PREVIEW COOLDOWN -----
        s.last_preview_time = 0
        s.preview_interval = 1.0  #SECONDS

        # ----- SOUND PREVIEW COOLDOWN -----
        s.preview_sound_timer = Timer(800, repeat = False)

    
    def update(s, delta_time):
        s.preview_sound_timer.update()


    # ----- MUSIC METHODS -----
    def play_for_state(s, state_name):
        track_name = s.state_music.get(state_name)
        if track_name:
            s.play_music(track_name)

    def play_music(s, track_name):
        if not s.music_on:
            mixer.music.stop()
            s.current_track = None
            return

        if track_name != s.current_track:
            track_path = s.game.music_tracks.get(track_name)
            if track_path:
                mixer.music.load(track_path)
                mixer.music.set_volume(s.music_volume)
                mixer.music.play(-1)
                s.current_track = track_name
                s.show_now_playing(track_name)
            else:
                mixer.music.stop()
                s.current_track = None

    def stop_music(s):
        mixer.music.stop()
        s.current_track = None

    def set_music_volume(s, volume):
        s.music_volume = volume
        mixer.music.set_volume(volume)
        s.game.audio_data['music_volume'] = volume
        save_data(s.game.audio_data, AUDIO_DATA_PATH)

    def toggle_music(s):
        s.music_on = not s.music_on
        s.game.audio_data['music_on'] = s.music_on
        save_data(s.game.audio_data, AUDIO_DATA_PATH)
        if not s.music_on:
            s.stop_music()
        else:
            s.play_for_state(s.game.state_manager.current_state)

    def show_now_playing(s, track_name):
        """Send a MusicPopUp to the StateManager to display."""
        popup = MusicPopUp(s.game, track_name, duration=3)
        s.game.state_manager.music_popups.add(popup)

    # ----- SOUND EFFECT METHODS -----
    def play_sound(s, sound):

        if not s.sound_on:
            return
        
        snd = sound
        if snd:
            snd.set_volume(s.sound_volume)
            snd.play()
        else:
            print(f'[SOUND ERROR]: {snd}')

    def set_sound_volume(s, volume):
        s.sound_volume = volume
        s.game.audio_data['sound_volume'] = volume
        save_data(s.game.audio_data, AUDIO_DATA_PATH)

        # Play preview sound only if the timer is inactive
        if not s.preview_sound_timer.active:
            s.play_sound(s.game.state_manager.states['Options menu'].test_sound)
            s.preview_sound_timer.activate()

    def toggle_sound(s):
        s.sound_on = not s.sound_on
        s.game.audio_data['sound_on'] = s.sound_on
        save_data(s.game.audio_data, AUDIO_DATA_PATH)

        s.play_sound(s.game.options_menu_sound)