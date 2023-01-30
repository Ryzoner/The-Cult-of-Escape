from configparser import ConfigParser, SectionProxy
from os.path import dirname, abspath
from locale import getdefaultlocale
from sqlite3 import connect

import pygame


class DataBase:
    '''Class for working with sqlite3 databases

    Initilization arguments: 
        *db_folder_path - Path to folder with databases regarding C://: str

    Methods:
        *execute - Execute sqlite3 query
        *get_text - Get dict with text on selected language (if it supported)
        *get_sounds - Get sounds list with tuples (path and pygame sound itself)
        *get_font - Return font with selected name
    '''
    __slots__ = ['sound_db_path', 'selected_db_path', 'font_db_path',
                 'text_db_path']

    def __init__(self, db_folder_path: str):
        self.sound_db_path: str = f'{db_folder_path}/sounds.db'
        self.font_db_path: str = f'{db_folder_path}/fonts.db'
        self.text_db_path: str = f'{db_folder_path}/text.db'
        self.selected_db_path = self.sound_db_path

    def execute(self, command: str) -> str:
        with connect(self.selected_db_path) as database:
            cur = database.cursor()
            result: str = cur.execute(command).fetchall()
        return result

    def get_text(self) -> dict:
        self.selected_db_path = self.text_db_path
        lang = getdefaultlocale()[0].split('_')[0].lower().strip()
        if lang not in ['ru', 'tr', 'en', 'az']:
            lang = 'en'
        result = self.execute(f'SELECT *\nFROM {lang}')[0]
        decryptor = {0: 'play', 1: 'shop', 2: 'faq', 3: 'settings',
                     4: 'faq_text', 5: 'fps'}
        return {decryptor[index]: title for index, title in enumerate(result)}

    def get_sounds(self) -> list([tuple, tuple, tuple, ...]):
        self.selected_db_path = self.sound_db_path
        return self.execute('SELECT *\nFROM sounds')

    def get_font(self, name) -> str:
        self.selected_db_path = self.font_db_path
        result = self.execute(
            f'SELECT path\nFROM fonts\nWHERE name = "{name}"')
        return result[0][0]


class Settings:
    '''Class wich can parse and save settings from setiings file (ext: .ini)

    Initilization arguments: 
        *settings_file_name - Path to settings file: str

    Methods:
        *all_settings - Parse all settings and return em
        *save - Write to settings given dictionary
    '''
    __slots__ = ['settings_path', 'settings_parser', 'settings']

    def __init__(self, settings_file_name: str):
        self.settings_path: str = f'./{settings_file_name}'
        self.settings_parser: ConfigParser = ConfigParser()
        self.settings = self.all_settings()

    def all_settings(self) -> dict:
        self.settings_parser.read(self.settings_path, encoding='utf-8')
        dirty_settings: SectionProxy = self.settings_parser[
            'TheCultofEscape']
        fps = int(dirty_settings['fps'])
        skin: str = dirty_settings['skin']
        window_size = list(
            map(int, dirty_settings['window_size'].split('x')))
        path: str = dirname(abspath(__file__))
        gravity = float(dirty_settings['gravity'])
        step = int(dirty_settings['step'])
        jump_power = int(dirty_settings['jump_power'])
        return {'fps': fps, 'path': path,
                'window_size': window_size,
                'skin': skin, 'gravity': gravity,
                'step': step, 'jump_power': jump_power}

    def save(self, new_settings: dict) -> None:
        for key in new_settings:
            self.settings_parser.set(
                'TheCultofEscape', key, new_settings[key])
        with open(self.settings_path, 'w', encoding='utf-8') as settings_file:
            self.settings_parser.write(settings_file)


class Sounds:
    '''Class for working with sqlite3 databases

    Initilization arguments: 
        *database - Path sound database: str

    Methods:
        *get_sounds - Return dict with all sounds from database
        *play - Play sound by name a certain times
        *stop - Stop playing selected sound
        *stop_all - Stop ALL sound

    '''
    __slots__ = ['database', 'sounds']

    def __init__(self, database):
        self.database = DataBase(database)
        self.sounds = self.get_sounds()

    def get_sounds(self) -> dict:
        sounds = self.database.get_sounds()
        return {name: {'path': path,
                       'sound': pygame.mixer.Sound(path)}
                for (name, path) in sounds}

    def play(self, name, loops=1) -> None:
        self.sounds[name]['sound'].play(loops)

    def stop(self, name) -> None:
        self.sounds[name]['sound'].stop()

    def stop_all(self) -> None:
        for name in self.sounds:
            self.sounds[name]['sound'].stop()
