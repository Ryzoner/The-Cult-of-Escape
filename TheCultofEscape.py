import pygame
from os.path import exists, dirname, abspath
from configparser import ConfigParser, SectionProxy
from time import time
from threading import Thread
from sqlite3 import connect

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()

SETTINGS_FILE = 'settings.ini'


class SpriteError(Exception):
    """Can't find sprite file"""
    
    def __init__(self):
        self.text = 'Не удается найти файл спрайта'
        

class Sprite:
    """
    Sprite class
    
    Methods:
        *set_group - add skin to group
        *to_spawn - move sprite to spawn position
        *teleport - teleport sprite to selected position
    """
    __slots__ = ['start_position', 'hp', 'skin', 'settings', 'skin_group',
                 'width', 'height', 'folder_path', 'skin_name']
    
    def __init__(self, position: list, hp: int, skin_name: str,
                 folder_path: str):
        self.start_position: list = position
        self.hp: int = hp
        self.skin_name: str = skin_name
        self.folder_path: str = folder_path
        self.settings: dict = Settings(SETTINGS_FILE).settings()
        
    def setup(self, full_file_path: str) -> None:
        self.skin: pygame.sprite.Sprite = self.set_skin(full_file_path)
        self.width: int = self.skin.image.get_width()
        self.height: int = self.skin.image.get_height()
        
    def set_group(self) -> None:
        self.skin_group = pygame.sprite.Group()
        self.skin_group.add(self.skin)
        
    def to_spawn(self) -> None:
        self.teleport(self.start_position)

    def teleport(self, position: list) -> None:
        self.skin.x, self.skin.y = position

    def full_file_path(self, skin_path: str) -> str:
        game_path: str = self.settings['path']
        sprite_folder = f'{game_path}/{self.folder_path}'
        full_skin_path = f'{sprite_folder}/{self.skin_name}/{skin_path}'
        return full_skin_path

    def set_skin(self, skin_path: str) -> pygame.sprite.Sprite:
        full_skin_path = self.full_file_path(skin_path)
        if not exists(full_skin_path):
            raise SpriteError
        sprite = pygame.sprite.Sprite()
        sprite.image = pygame.image.load(full_skin_path)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x, sprite.rect.y = self.start_position
        return sprite

    def change_skin(self, skin_path: str) -> pygame.sprite.Sprite:
        full_skin_path = self.full_file_path(skin_path)
        if not exists(full_skin_path):
            raise SpriteError
        x, y = self.skin.rect.x, self.skin.rect.y
        self.skin.image = pygame.image.load(full_skin_path)
        self.skin.rect = self.skin.image.get_rect()
        self.skin.rect.x, self.skin.rect.y = x, y

    def is_in_window(self, position: list) -> bool:
        x: int = position[0]
        y: int = position[1]
        if x not in range(self.settings['window_size'][0] + self.width):
            return False
        if y not in range(self.settings['window_size'][1] + self.height):
            return False
        return True


class DataBase:
    __slots__ = ['sound_db_path', 'selected_db_path']

    def __init__(self, db_folder_path: str):
        self.sound_db_path: str = f'{db_folder_path}/sounds.db'

    def execute(self, command: str) -> str:
        with connect(self.selected_db_path) as db:
            cur = db.cursor()
            result: str = cur.execute(command).fetchall()
        return result

    def get_sounds(self) -> list([tuple, tuple, tuple, ...]):
        self.selected_db_path = self.sound_db_path
        return self.execute('SELECT *\nFROM sounds')


class Sounds:
    __slots__ = ['db', 'sounds']

    def __init__(self, database):
        self.db = DataBase(database)
        self.sounds = self.get_sounds()

    def get_sounds(self) -> dict:
        sounds = self.db.get_sounds()
        return {name: {'path': path,
                       'sound': pygame.mixer.Sound(path)}
                for (name, path) in sounds}

    def play(self, name, loops=1) -> None:
        self.sounds[name]['sound'].play(loops)


class Settings:
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
        backround_color: str = dirty_settings['backround_color']
        window_size = list(
            map(int, dirty_settings['window_size'].split('x')))
        path: str = dirname(abspath(__file__))
        return {'fps': fps, 'path': path,
                'background_color': backround_color,
                'window_size': window_size,
                'skin': skin}


class Player(Sprite):
    __slots__ = ['skin', 'jump_count', 'jump_time', 'last_stand_func_call',
                 'state', 'sounds', 'skins', 'jump_start']

    def __init__(self, position: list, hp: int, skin_name: str):
        super().__init__(position, hp, skin_name, 'assets/sprites/santa')
        self.skin: pygame.sprite.Sprite = self.set_player_skin('stand')
        self.setup(self.get_skins()['stand'])
        self.skins = self.get_skins()
        self.jump_count, self.jump_time = 10, 0.1
        self.last_stand_func_call = 0
        self.jump_start = 0
        self.state: dict = {'sit': False, 'jump': False, 'flip': False,
                            'flip_counter': 0}
        music_db_path: str = self.settings['path'] + '/assets/database/'
        self.sounds = Sounds(music_db_path)
        self.to_spawn()
        self.set_group()

    def set_player_skin(self, skin_type: str = '') -> pygame.sprite.Sprite:
        return self.set_skin(self.get_skins()[skin_type])

    def change_player_skin(self, skin_type: str = '') -> None:
        return self.change_skin(self.get_skins()[skin_type])

    def get_skins(self) -> dict:
        skin_file_name_stand = f'santa_{self.skin_name}_skin.png'
        skin_file_name_sit = f'santa_{self.skin_name}_sit_skin.png'
        skin_file_name_jump = f'santa_{self.skin_name}_jump_skin.png'
        skins = {'stand': skin_file_name_stand,
                 'sit': skin_file_name_sit,
                 'jump': skin_file_name_jump}
        return skins

    def die(self) -> None:
        self.hp -= 1
        self.to_spawn()
        self.sounds.play('die')

    def turn(self, direction: str) -> None:
        if not self.state['flip'] and direction == 'left':
            self.flip()
        if self.state['flip'] and direction == 'right':
            self.flip()

    def move(self, direction: str) -> None:
        i = 1 if self.state['jump'] else 5
        if self.state['sit']:
            return self.turn(direction)
        if direction == 'right':
            if self.is_in_window([self.skin.rect.x + i, self.skin.rect.y]):
                self.skin.rect.x += i
            else:
                return
            if self.state['flip']:
                self.flip()
        elif direction == 'left':
            if self.is_in_window([self.skin.rect.x - i, self.skin.rect.y]):
                self.skin.rect.x -= i
            else:
                return
            if not self.state['flip']:
                self.flip()
        self.sounds.play('step')

    def flip(self) -> None:
        self.skin.image = pygame.transform.flip(
            self.skin.image, True, False)
        self.state['flip'] = not self.state['flip']
        self.state['flip_counter'] += 1

    def fix_jump(self) -> None:
        pygame.key.set_repeat(1, 1)
        if self.state['jump']:
            return
        self.state['jump'] = True
        self.jump_start = self.skin.rect.y
        self.change_player_skin('jump')
        pygame.mixer.stop()
        self.sounds.play('jump')

    def sit(self) -> None:
        if not (self.state['sit'] or self.state['jump']):
            self.state['sit'] = True
            self.change_player_skin('sit')
            if self.state['flip']:
                self.flip()

    def stand(self) -> None:
        if self.state['sit']:
            self.state['sit'] = False
            self.last_stand_func_call = time()
            self.change_player_skin('stand')
            if self.state['flip']:
                self.flip()
        else:
            if time() - self.last_stand_func_call > 0.3:
                self.fix_jump()

    def jump(self) -> None:
        if self.jump_count >= -10:
            speed_direction = -1 if self.jump_count < 0 else 1
            if self.state['flip']:
                self.flip()
            self.skin.rect.y -= speed_direction * \
                ((self.jump_count ** 2) / 2)
            self.jump_count -= 1
        else:
            self.jump_count = 10
            self.skin.rect.y = self.jump_start
            self.state['jump'] = False
            pygame.key.set_repeat(1, 100)
            self.state['sit'] = True
            self.stand()


class Game:
    def __init__(self, settings: dict):
        self.running = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.settings: dict = settings
        self.fps = self.settings['fps']
        pygame.key.set_repeat(1, 100)

    def get_screen(self, window_size: list) -> pygame.Surface:
        screen: pygame.Surface = pygame.display.set_mode(window_size)
        pygame.display.set_caption('The Cult of Escape')
        return screen

    def event_handler(self, event: pygame.event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.santa.move('right')
            if keys[pygame.K_LEFT]:
                self.santa.move('left')
            if keys[pygame.K_DOWN]:
                self.santa.sit()
            if keys[pygame.K_UP]:
                self.santa.stand()

    def start(self):
        self.santa: Player = Player(
            [0, self.settings['window_size'][1] - 16], 2,
            self.settings['skin'])
        self.screen = self.get_screen(self.settings['window_size'])
        while self.running:
            for event in pygame.event.get():
                self.event_handler(event)
            if self.santa.state['jump']:
                self.santa.jump()
            self.clock.tick(self.fps)
            self.screen.fill((0, 0, 0))
            self.draw_level()
            pygame.display.update()
        pygame.quit()
        exit()

    def draw_level(self):
        self.santa.skin_group.draw(self.screen)


game = Game(Settings('settings.ini').settings)
game.start()