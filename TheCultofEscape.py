import pygame
from os.path import exists, dirname, abspath
from configparser import ConfigParser, SectionProxy
from time import time
from threading import Thread

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()

SETTINGS_FILE = 'settings.ini'

class Player:

    def __init__(self, position: list,
                 hp: int = 20,
                 skin_name: str = "red"):
        self.jumpCount = 10
        self.last_stand_func_call = 0
        self.start_position: list = position
        self.skin_name: str = skin_name
        self.hp: int = hp
        self.state: dict = {'sit': False, 'jump': False, 'flip': False,
                            'flip_counter': 0}
        self.settings: dict = Settings(SETTINGS_FILE).settings
        music_path: str = self.settings['path'] + '/assets/audio'
        self.sounds: dict = {
             'move': pygame.mixer.Sound(f'{music_path}/step.mp3'),
             'die': pygame.mixer.Sound(f'{music_path}/die.mp3')}
        self.skin: pygame.sprite.Sprite = self.set_skin(skin_name)
        self.to_spawn()
        self.set_group()
        
        
    def set_group(self):
        self.skin_group = pygame.sprite.Group()
        self.skin_group.add(self.skin)

    def set_skin(self, skin_name: str, skin_type: str = ''):
        game_path: str = self.settings["path"]
        skin_file_name: str = f'santa_{skin_name}_skin.png'
        skin_name: str = skin_name.rstrip(skin_type + '_')
        santa_path: str = 'assets/sprites/santa'
        skin_path: str = f'{game_path}/{santa_path}/{skin_name}/{skin_file_name}'
        if not exists(skin_path):
            return self.set_skin('red')
        sprite = pygame.sprite.Sprite()
        sprite.image = pygame.image.load(skin_path)

        sprite.image.set_colorkey(pygame.Color('white'))
        sprite.image = pygame.transform.scale(sprite.image, (32, 32))
        sprite.rect = sprite.image.get_rect()

        return sprite

    def die(self):
        self.hp -= 1
        self.to_spawn()
        self.sounds['die'].play()
        
    def to_spawn(self):
        self.teleport(self.start_position)
        
    def teleport(self, position: list):
        self.skin.x, self.skin.y = position
        
    def is_in_window(self, position: list):
        if position[0] not in range(self.settings['window_size'][0] + 32):
            return False
        elif position[1] not in range(self.settings['window_size'][1] + 32):
            return False
        return True
    
    def flip(self):
         self.skin.image = pygame.transform.flip(self.skin.image,
                                                 True, False)
        self.state['flip'] = not self.state['flip']
        self.state['flip_counter'] += 1
        
    def sit(self):
        if not (self.state['sit'] or self.state['jump']):
            x, y = self.skin.rect.x, self.skin.rect.y
            self.skin = self.set_skin(self.skin_name + "_sit", 'sit')
            self.skin.rect.x, self.skin.rect.y = x, y
            self.set_group()
            if self.state['flip']:
                self.flip()
            self.state['sit'] = True

    def stand(self):
        if self.state['sit']:
            self.last_stand_func_call = time()
            x, y = self.skin.rect.x, self.skin.rect.y
            self.skin = self.set_skin(self.skin_name)
            self.skin.rect.x, self.skin.rect.y = x, y
            self.set_group()
            self.state['sit'] = False
            if self.state['flip']:
                self.flip()
            else:
                if time() - self.last_stand_func_call > 0.3:
                    self.jump()
                                              
    def jump(self):
        if not self.state['jump']:
            self.state['jump'] = True
            x, y = self.skin.rect.x, self.skin.rect.y
            self.skin = self.set_skin(self.skin_name + "_jump", 'jump')
            self.skin.rect.x, self.skin.rect.y = x, y
            self.set_group()
            
    def draw_jump(self):
        if self.jumpCount >= -10:
            neg = 1
            if self.state['flip']:
                self.flip()
            if self.jumpCount < 0:
                neg -= 1
            self.skin.rect.y -= self.jumpCount ** 2 * 0.1 * neg
            self.jumpCount -= 1
        else:
            self.jumpCount = 10
            self.state['jump'] = False
            self.state['sit'] = True
            self.stand()
            
    def move(self, direction: str):
        if not self.state['sit']:
            if direction == 'right':
                if self.state['flip']:
                    self.flip()
                if self.is_in_window([self.skin.rect.x + 1, self.skin.rect.y]):
                    self.skin.rect.x += 5
            elif direction == 'left':
                if not self.state['flip']:
                    self.flip()
                if self.is_in_window([self.skin.rect.x - 1, self.skn.rect.t]):
                    self.skin.rect.x -= 5
            self.sounds['move'].play()
        else:
            if not self.state['flip'] and direction == 'left':
                self.flip()
            if self.state['flip'] and direction == 'right':
                self.flip()

class Level:
    __slots__ = ["name", "difficulty"]

    def __init__(self, name: str, difficulty: str):
        self.name = name
        self.difficulty = difficulty


class Settings:
    __slots__ = ['settings_path', 'settings_parser', 'settings']
    
    def __init__(self, settings_file_name: str):
        self.settings_path: str = f"./{settings_file_name}"
        self.settings_parser: ConfigParser = ConfigParser()
        self.all_settings()

    def all_settings(self):
        self.settings_parser.read(self.settings_path, encoding="utf-8")
        dirty_settings: SectionProxy = self.settings_parser["TheCultofEscape"]
        fps = int(dirty_settings["fps"])
        skin: str = dirty_settings['skin']
        backround_color: str = dirty_settings["backround_color"]
        window_size = list(
            map(int, dirty_settings["window_size"].split("x")))
        path: str = dirname(abspath(__file__))
        self.settings = {
            "fps": fps,
            "path": path,
            "background_color": backround_color,
            "window_size": window_size,
            "skin": skin
        }


class Game:
    
    def __init__(self, settings: dict):
        self.running = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.settings: dict = settings
        
    def get_screen(self, window_size: list):
        screen: pygame.Surfece = pygame.display.set_mode(window_size)
        pygame.display.set_caption("The Cult of Escape")
        return screen
    
    def start(self):
        self.player: Player = Player([0, 100 - 32], 2, self.settings['skin'])
        self.screen = self.get_screen(self.settings['window_size'])
        fps = self.settings['fps']
        background_color = self.settings['background_color']
        pygame.key.set_repeat(1, 100)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        self.player.move('left')
                    if keys[pygame.K_RIGHT]:
                        self.player.move('right')
                    if keys[pygame.K_UP]:
                        self.player.stand()
                    if keys[pygame.K_DOWN]:
                        self.player.sit()
            if self.player.state['jump']:
                self.player.draw_jump()
                
            """
            block_hit_list = pygame.sprite.spritecollide(self.player,
                                                        self.traps,
                                                        True)
            """
            self.clock.tick(fps)
            self.screen.fill(background_color)
            self.run_main_window()
            pygame.display.update()
        pygame.quit()
        exit()
    
    def run_main_window(self):
        self.player.skin_group.draw(self.screen)
        

game = Game(Settings('settings.ini').settings)
game.start()
