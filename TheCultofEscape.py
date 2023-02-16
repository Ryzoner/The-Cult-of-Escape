# -*- coding: utf-8 -*-

from Levels import FirstLevel, SecondLevel, ThirdLevel, FourthLevel
from Window import MainWindow, LoseWindow, EndWindow
from Utils import Settings, Sounds

import pygame

pygame.mixer.pre_init(44100, -8, 2, 512)
pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(10)

SETTINGS_FILE = 'settings.ini'


class GameManager:
    '''Main game class which launch game and control levels and windows
    Initilization arguments: 
        *settings - Dict with settings from class Settings: dict
    Methods:
        *start - Start game manager and get game class -> None
        *run_game - Launch game -> None
        *next_level - Launch next level -> None
    '''
    __slots__ = ['settings', 'level_number', 'hit_points', 'game', 'levels',
                 'windows', 'sounds']

    def __init__(self, settings: dict):
        self.settings: dict = settings
        self.level_number: int = 1
        db_path: str = self.settings['path'] + '/assets/database/'
        self.sounds = Sounds(db_path)
        self.levels = {1: FirstLevel, 2: SecondLevel, 3: ThirdLevel,
                       4: FourthLevel}
        self.windows = {'main_window': [MainWindow, self.settings],
                        'level': [FirstLevel, self.settings, 10],
                        'lose': [LoseWindow, self.settings],
                        'end': [EndWindow, self.settings]}

    def start(self, mode: str = '') -> None:
        '''
        Arguments:
            mode - type of window: str
        '''
        if mode == 'lose':
            self.level_number = 1
        if mode == 'win':
            self.game = self.next_level()
        else:
            self.game = self.windows[mode][0](*self.windows[mode][1:])
        self.run_game()

    def next_level(self):
        self.level_number += 1
        if self.level_number in list(self.levels.keys()):
            return self.levels[self.level_number](
                self.settings, self.game.santa.hit_points)
        self.level_number = 1
        return self.windows['end'][0](*self.windows['end'][1:])

    def run_game(self) -> None:
        start_mode = self.game.mode
        self.game.game_cycle()
        if self.game.mode != start_mode:
            new_mode = self.game.mode
            if new_mode in ['win', 'level']:
                try:
                    self.hit_points = self.game.santa.hit_points
                except Exception:
                    self.hit_points = 10
            self.start(new_mode)


if __name__ == "__main__":
    app = GameManager(Settings(SETTINGS_FILE).settings)
    app.start('main_window')
pygame.quit()
