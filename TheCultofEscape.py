from Window import MainWindow
from Levels import FirstLevel, SecondLevel, ThirdLevel
from Utils import Settings

import pygame

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(20)

SETTINGS_FILE = 'settings.ini'


class GameManager:
    '''Main game class which launch game and control levels and windows
    Initilization arguments: 
        *settings - Dict with settings from class Settings: dict
    Methods:
        *start - Start game manager and get game class -> None
        *run_game - Launch game -> None
    '''
    __slots__ = ['settings', 'level_number', 'hit_points', 'game', 'levels']

    def __init__(self, settings: dict):
        self.settings: dict = settings
        self.level_number: int = 1
        self.levels = {2: FirstLevel, 3: SecondLevel, 5: ThirdLevel}

    def start(self, mode: str = '') -> None:
        '''
        Arguments:
            mode - type of window
        '''
        if mode == 'main_window':
            self.game = MainWindow(self.settings)
        elif mode == 'settings':
            self.game = SettingsWindow(self.settings)
        elif mode == 'level':
            self.game = FirstLevel(self.settings, 10)
        elif mode == 'win':
            self.level_number += 1
            self.game = self.next_level()
        elif mode == 'lose':
            self.level_number = 1
            self.game = LoseWindow(self.settings)
        self.run_game()
        
    def next_level(self):
        self.level_number += 1
        hit_points = self.game.santa.hit_points
        return self.levels[self.level_number](self.settings, hit_points)

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