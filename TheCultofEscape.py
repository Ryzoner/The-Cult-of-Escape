''' Main game file, manage windows and catch errors '''
import logging

import pygame

from Levels import FifthLevel, FirstLevel, FourthLevel, SecondLevel, ThirdLevel
from Utils import Settings
from Window import EndWindow, LoseWindow, MainWindow, ShopWindow

SETTINGS_FILE = 'settings.ini'

# pygame initilization
pygame.mixer.pre_init(44100, -8, 2, 512)
pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(10)

# logging initilization
logging.basicConfig(
    filename='./error_log.txt', filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S', level=logging.DEBUG)


class GameManager:
    '''Main game class which launch game and control levels and windows
    Initilization arguments:
        *settings - Dict with settings from class Settings: dict
    Methods:
        *start - Start game manager and get game class -> None
        *run_game - Launch game -> None
        *next_level - Launch next level
    '''
    __slots__ = ['settings', 'level_number', 'hit_points', 'game', 'levels',
                 'windows']

    def __init__(self, settings: dict):
        self.settings: dict = settings
        self.level_number: int = 1
        self.hit_points: int = 10
        self.levels: list = [None, FirstLevel, SecondLevel, ThirdLevel,
                             FourthLevel, FifthLevel]
        self.windows: dict = {
            'main_window': [MainWindow, self.settings],
            'level': [self.levels[1], self.settings, 10],
            'lose': [LoseWindow, self.settings],
            'end': [EndWindow, self.settings],
            'shop_window': [ShopWindow, Settings(SETTINGS_FILE)]}

    def start(self, mode: str = '') -> None:
        '''
        Arguments:
            mode - type of window: str
        '''
        if mode in {'lose', 'level'}:
            self.level_number = 1
        if mode == 'win':
            self.game = self.next_level()
        else:
            self.game = self.windows[mode][0](*self.windows[mode][1:])
        self.run_game()

    def next_level(self):
        if self.level_number in range(1, len(self.levels) - 1):
            self.level_number += 1
            return self.levels[self.level_number](
                self.settings, self.game.santa.hit_points)
        self.level_number = 1
        return self.windows['end'][0](*self.windows['end'][1:])

    def run_game(self) -> None:
        start_mode: str = self.game.mode
        self.game.game_cycle()
        if self.game.mode != start_mode:
            new_mode = 'level' if self.game.mode == 'replay' else self.game.mode
            if new_mode in ['win', 'level']:
                try:
                    self.hit_points: int = self.game.santa.hit_points
                except AttributeError:
                    self.hit_points = 10
            self.start(new_mode)


def count_launch():
    updated_number_of_games = str(
        settings_manager.settings['number_of_games'] + 1)
    settings_manager.save({'number_of_games': updated_number_of_games})


settings_manager = Settings(SETTINGS_FILE)
count_launch()

if __name__ == "__main__":
    game_manager = GameManager(settings_manager.settings)
    try:
        game_manager.start('main_window')
    except Exception as error:
        # writing error info in ./error_log.txt
        logging.exception(error, exc_info=True)

pygame.quit()
