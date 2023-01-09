import pygame
from os.path import exists, dirname, abspath
from configparser import ConfigParser

pygame.init()


class Santa:
    __slots__ = ["hp", "skin", "settings", "skin_group"]

    def __init__(self, hp, position, skin_name="red"):
        self.hp = hp
        self.settings = Settings("settings.ini").settings
        self.skin = self.set_skin(skin_name)
        self.skin.rect = self.skin.image.get_rect()
        x, y = position
        self.skin_group = pygame.sprite.Group()
        self.skin.rect.x = x
        self.skin.rect.y = y
        self.skin_group.add(self.skin)

    def set_skin(self, skin_name):
        game_path = self.settings["path"]
        skin_file_name = f"santa_{skin_name}_skin.png"
        skin_path = f"{game_path}/assets/sprites/santa/{skin_name}/{skin_file_name}"
        if not exists(skin_path):
            return self.set_skin("red")
        sprite = pygame.sprite.Sprite()
        sprite.image = pygame.image.load(skin_path)
        sprite.image.set_colorkey(pygame.Color("white"))
        sprite.image = pygame.transform.scale(sprite.image, (32, 32))
        return sprite

    def die(self):
        self.hp -= 1


class Level:
    __slots__ = ["name", "difficulty"]

    def __init__(self, name: str, difficulty: str):
        self.name = name
        self.difficulty = difficulty


class StartGame:
    __slots__ = ["running", "clock", "settings", "screen", "santa"]

    def __init__(self, settings: dict):
        self.running = True
        self.clock = pygame.time.Clock()
        self.settings = settings

    def get_screen(self, window_size: list):
        screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Christmas Adventures")
        return screen

    def start(self):
        self.santa = Santa(2, [0, 0], "thief")
        self.screen = self.get_screen(self.settings["window_size"])
        fps = self.settings["fps"]
        background_color = self.settings["background_color"]
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.clock.tick(fps)
            self.screen.fill(background_color)
            self.run_main_window()
            pygame.display.update()
        pygame.quit()
        exit()

    def run_main_window(self):
        self.santa.skin_group.draw(self.screen)


class Settings:
    def __init__(self, settings_file_name: str):
        self.settings_path = f"./{settings_file_name}"
        self.settings_parser = ConfigParser()
        self.all_settings()

    def all_settings(self):
        self.settings_parser.read(self.settings_path, encoding="utf-8")
        dirty_settings = self.settings_parser["ChristmasAdventures"]
        fps = int(dirty_settings["fps"])
        backround_color = dirty_settings["backround_color"]
        window_size = list(map(int, dirty_settings["window_size"].split("x")))
        path = dirname(abspath(__file__))
        self.settings = {
            "fps": fps,
            "path": path,
            "background_color": backround_color,
            "window_size": window_size,
        }


game = StartGame(Settings("settings.ini").settings)
game.start()
