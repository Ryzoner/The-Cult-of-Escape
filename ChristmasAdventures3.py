from os.path import exists, dirname, abspath
from configparser import ConfigParser, SectionProxy
from time import time
from sqlite3 import connect

import pygame_gui
import pygame

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()

SETTINGS_FILE = 'settings.ini'

class SpriteError(Exception):
    '''Can't find sprite file'''
    __slots__ = ['text']

    def __init__(self):
        super().__init__()
        self.text = 'Не удаётся найти файл спрайта'


class Sprite:
    '''Base sprite class

    Initilization arguments: 
        *position - Start position of sprite : str
        *hit_points - Count of sprite lifes : int
        *skin_name - Opted skin : str
        *folder_path - Sprite folder path regarding game path: str

    Methods:
        *setup - Declaration of variables lika skin, height, width
        *set_group - Add skin to group
        *to_spawn - Move sprite to start position
        *teleport - Teleport sprite to selected position
        *full_file_path - Full sprite path
        *set_skin - Set sprite image
        *change_skin - Update sprite image
        *is_in_window - Check position in window or not
    '''
    __slots__ = ['start_position', 'hit_points', 'skin', 'settings',
                 'skin_group', 'width', 'height', 'folder_path', 'skin_name']

    def __init__(self, position: list, hit_points: int, skin_name: str,
                 folder_path: str):
        self.start_position: list = position
        self.hit_points: int = hit_points
        self.skin_name: str = skin_name
        self.folder_path: str = folder_path
        self.settings: dict = Settings(SETTINGS_FILE).settings

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
        return f'{sprite_folder}/{self.skin_name}/{skin_path}'

    def set_skin(self, skin_path: str) -> pygame.sprite.Sprite:
        full_skin_path = self.full_file_path(skin_path)
        if not exists(full_skin_path):
            raise SpriteError
        sprite = pygame.sprite.Sprite()
        sprite.image = pygame.image.load(full_skin_path).convert_alpha()
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x, sprite.rect.y = self.start_position
        sprite.mask = pygame.mask.from_surface(sprite.image)
        return sprite

    def change_skin(self, skin_path: str) -> pygame.sprite.Sprite:
        full_skin_path = self.full_file_path(skin_path)
        if not exists(full_skin_path):
            raise SpriteError
        current_position = (self.skin.rect.x, self.skin.rect.y)
        self.skin.image = pygame.image.load(full_skin_path)
        self.skin.rect = self.skin.image.get_rect()
        self.skin.rect.x, self.skin.rect.y = current_position

    def is_in_window(self, position: list) -> bool:
        x: int = position[0]
        if x not in range(self.settings['window_size'][0] + self.width):
            return False
        y: int = position[1]
        return y in range(self.settings['window_size'][1] + self.height)


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
        result = self.execute('SELECT *\nFROM tr')[0]
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
        return {'fps': fps, 'path': path,
                'window_size': window_size,
                'skin': skin,
                '_settings_path': self.settings_path}

    def save(self, new_settings: dict) -> None:
        for key in new_settings:
            self.settings_parser.set(
                'TheCultofEscape', key, new_settings[key])
        with open(self.settings_path, 'w', encoding='utf-8') as settings_file:
            self.settings_parser.write(settings_file)


class Player(Sprite):
    '''Player, the main face of the game  which can move, turn, jump,
       change skin, die
    
    Initilization arguments: 
        *position - Start position of sprite : str
        *hit_points - Count of sprite lifes : int
        *skin_name - Opted skin : str

    Methods:
        *change_player_skin - Change player skin
        *get_skins - Return dictionary with aviable skins
        *die - Play die sound, takes away one hit_point and teleport player to
               spawn
        *turn - Turn player to selected direction
        *move - Move player to right or left
        *flip - Turn player around himself
        *fix_jump - Fix that player jumped and start jump
        *sit - Make player sit (dodge)
        *stand - Returns player to standing position
        *jump - Make player jump
        *stop_jumping - Stop jumping
    '''
    __slots__ = ['skin', 'jump_time', 'last_stand_func_call',
                 'state', 'sounds', 'skins', 'jump_start']

    def __init__(self, position: list, hit_points: int, skin_name: str):
        super().__init__(position, hit_points, skin_name, 'assets/sprites/santa')
        self.skin: pygame.sprite.Sprite = self.set_skin(
            self.get_skins()['stand'])
        self.setup(self.get_skins()['stand'])
        self.skins = self.get_skins()
        self.jump_time = 0.1
        self.last_stand_func_call = 0
        self.jump_start = 0
        self.state: dict = {
            'sit': False, 'jump': False, 'flip': False, 'jump_count': 10,
            'on_earth': False}
        db_path: str = self.settings['path'] + '/assets/database/'
        self.sounds = Sounds(db_path)
        self.to_spawn()
        self.set_group()

    def change_player_skin(self, skin_type: str = '') -> None:
        return self.change_skin(self.get_skins()[skin_type])

    def get_skins(self) -> dict:
        skin_file_name_stand = f'santa_{self.skin_name}_skin.png'
        skin_file_name_sit = f'santa_{self.skin_name}_sit_skin.png'
        skin_file_name_jump = f'santa_{self.skin_name}_jump_skin.png'
        return {
            'stand': skin_file_name_stand,
            'sit': skin_file_name_sit,
            'jump': skin_file_name_jump,
        }

    def die(self) -> None:
        self.to_spawn()
        self.sounds.stop('step')
        self.sounds.play('die')
        self.hit_points -= 1

    def turn(self, direction: str) -> None:
        if not self.state['flip'] and direction == 'left':
            self.flip()
        elif self.state['flip'] and direction == 'right':
            self.flip()

    def move(self, direction: str, all_sprites) -> None:
        step = 1 if self.state['jump'] else 5
        if self.state['sit']:
            return self.turn(direction)
        elif direction == 'right':
            self.skin.rect.x += step
            if self.is_collide(all_sprites):
                self.skin.rect.x -= step
                return
            if self.state['flip']:
                self.flip()
        elif direction == 'left':
            self.skin.rect.x -= step
            if self.is_collide(all_sprites):
                self.skin.rect.x += step
                return
            if not self.state['flip']:
                self.flip()
        self.sounds.play('step')

    def flip(self) -> None:
        flip = pygame.transform.flip
        self.skin.image = flip(self.skin.image, True, False)
        self.state['flip'] = not self.state['flip']

    def fix_jump(self) -> None:
        pygame.key.set_repeat(1, 1)
        if self.state['jump']:
            return
        self.state['jump'] = True
        self.jump_start = self.skin.rect.y
        self.change_player_skin('jump')
        self.sounds.stop_all()
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
        elif time() - self.last_stand_func_call > 0.3:
            self.fix_jump()

    def jump(self, all_sprites, screen) -> None:
        if self.state['jump_count'] >= -10:
            speed_direction = -1 if self.state['jump_count'] < 0 else 1
            jump_height = speed_direction * \
                ((self.state['jump_count'] ** 2) / 2)
            self.skin.rect.y -= jump_height
            if self.is_collide(all_sprites):
                self.stop_jumping(all_sprites, screen)
            self.state['jump_count'] -= 1
        else:
            self.stop_jumping(all_sprites, screen)

    def stop_jumping(self, all_sprites, screen):
        self.state['jump'] = False
        self.state['sit'] = True
        pygame.key.set_repeat(1, 100)
        self.skin.rect.y = self.jump_start
        self.update(all_sprites)
        self.state['jump_count'] = 10
        self.stand()

    def is_collide(self, sprite_group):
        return any(
            pygame.sprite.collide_mask(self.skin, sprite)
            for sprite in sprite_group
        )

    def update(self, all_sprites):
        while self.is_collide(all_sprites):
            self.skin.rect.y -= 0.1
            self.skin.update()

    def gravity(self, all_sprites):
        if not self.is_collide(all_sprites) and not self.state['on_earth']:
            self.skin.rect.y += 20
            self.skin.update()
        if self.is_collide(all_sprites) and not self.state['on_earth']:
            self.skin.rect.y -= 15
            self.state['on_earth'] = True
        


class Window:
    '''Base window class
    
    Initilization arguments: 
        *settings - Settings from 'Settings.setting' class: dict
        *mode - Mode of window //examples 'main_window', 'login_window' 
                and etc : str

    Methods:
        *get_screen - Return window with selected title and size: pygame.Surface 
    '''
    __slots__ = ['settings', 'fps', 'mode', 'background_filler',
                 'text_filler', 'clock', 'screen', 'manager',
                 'database', 'gui_tools']

    def __init__(self, settings: dict, mode: str):
        pygame.event.set_allowed(
            [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.KEYUP,
             pygame.USEREVENT, pygame.MOUSEBUTTONUP])
        pygame.key.set_repeat(1, 100)
        self.settings: dict = settings
        self.gui_tools = GUI(settings)
        self.manager = self.gui_tools.manager
        db_path = f'{self.settings["path"]}/assets/database/'
        self.database = DataBase(db_path)
        self.fps = self.settings['fps']
        self.mode = mode
        background_path = self.settings['path'] + \
            '/assets/sprites/background/background.png'
        self.background_filler = pygame.image.load(background_path)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        icon_path = '/assets/sprites/icons/window_icons/icon_standart.png'
        icon = pygame.image.load(self.settings['path'] + icon_path)
        pygame.display.set_icon(icon)
        self.screen = self.get_screen(
            'The Cult of Escape', self.settings['window_size'])

    def get_screen(self, title: str, window_size: list) -> pygame.Surface:
        flags = pygame.DOUBLEBUF
        screen: pygame.Surface = pygame.display.set_mode(window_size, flags)
        screen.set_alpha(None)
        pygame.display.set_caption(title)
        return screen


class Button(pygame_gui.elements.UIButton):
    '''Base button class
    
    Initilization arguments: 
        *text - Button text: str
        *code_name - Special name for button for identefication: str
        *manager - pygame_gui manager: pygame_gui.UIManager
        *position - Button position on screen [x, y]: list
        *size - Button size [w, h]: list
        
    Methods:
        *load_icon - Load image and crop it to standart sizes: pygame.Surface
        *set_icon - Set icon for button: None
        *get_rect - Get button rect wich have x, y, w and h: pygame.Rect
        *move - Just move button to selected position: None
        *is_pressed - Check is button pressed or not: bool
    '''
    __slots__ = ['code_name']
    def __init__(self, text: str, code_name: str, manager: pygame_gui.UIManager,
                 position: list, size: list = None):
        if size is None:
            size = [50, 50]
        relative_rect = self.get_rect((*position,), (*size,))
        super().__init__(relative_rect=relative_rect, text=text,
                         manager=manager)
        self.code_name = code_name

    def load_icon(self, icon_path) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load(icon_path), [50, 50])
    
    def set_icon(self, icon_path) -> None:
        icon_extension = '.' + icon_path.split('.')[-1]
        hovered_icon_path = '.'.join(icon_path.split(icon_extension)[:-1]) + '_pressed' +\
            icon_extension
        icon =self.load_icon(icon_path)
        hovered_icon = self.load_icon(hovered_icon_path)
        self.normal_image = self.selected_image = icon
        self.hovered_image = hovered_icon
        self.rebuild()
    
    def get_rect(self, position: list, size: list) -> pygame.Rect:
        return pygame.Rect((*position,), (*size,))

    def move(self, position: list) -> None:
        self.rect.x = position[0]
        self.rect.y = position[1]
        
    def is_pressed(self, event: pygame.event) -> bool:
        return (
            event.user_type == pygame_gui.UI_BUTTON_PRESSED
            and event.ui_element == self
        )
    
class Label(pygame_gui.elements.UIButton):
    '''Base label class
    
    Initilization arguments: 
        *text - Label text: str
        *code_name - Special name for label for identefication: str
        *manager - pygame_gui manager: pygame_gui.UIManager
        *position - Label position on screen [x, y]: list
        *size - Label size [w, h]: list
        
    Methods:
        *connect_to_button - Connects label to button
        *move - Just label button to selected position: None
    '''
    __slots__ = ['code_name']
    def __init__(self, text: str, code_name: str, manager: pygame_gui.UIManager,
                 position: list, size: list):
        label_rect = pygame.Rect((position), (size))
        super().__init__(label_rect, text, manager)
        self.code_name = code_name

    def move(self, position: list) -> None:
        self.rect.x=position[0]
        self.rect.y=position[1]

    def connect_to_button(self, button: pygame_gui.elements.UIButton,
                          window_size: list, label_w: int) -> None:
        label_x = button.rect.x + 46
        label_y = window_size[1] - 55
        label_w = label_w - button.rect.w - 5
        label_h = button.rect.h
        label_rect = pygame.Rect((label_x, label_y), (label_w, label_h))
        self.rect = label_rect
        main_color = self.colours['normal_bg']
        for theme in self.colours:
            if 'text' not in theme:
                self.colours[theme] = main_color
        self.rebuild()

class Message(pygame_gui.windows.UIMessageWindow):
    '''Base Message (Message box) class
    
    Initilization arguments: 
        *text - Message text: str
        *code_name - Special name for Message box for identefication: str
        *manager - pygame_gui manager: pygame_gui.UIManager
        *position - Message box window position on screen [x, y]: list
        *size - Message box window size [w, h]: list
        *title - Message box window title: str
        
    Methods:
        *is_alive - Check is window alive
    '''
    __slots__ = ['code_name']
    def __init__(self, text: str, code_name: str, manager: pygame_gui.UIManager,
                 position: list, size: list, title: str):
        rect = pygame.Rect((position), (size))
        super().__init__(rect=rect, window_title=title, html_message=text,
                         manager=manager)
        self.dismiss_button.text = 'Ok'
        self.dismiss_button.rebuild()
        self.code_name = code_name

    def is_alive(self) -> bool:
        return not self.dismiss_button.pressed and not self.close_window_button.pressed
    
class Text(pygame.font.Font):
    '''Class for showing text on screen
    
    Initilization arguments: 
        *text - Text which you wanna display: str
        *code_name - Special name for Text object for identefication: str
        *position - Text position on screen [x, y]: list
        *settings - Dict with settings from class Settings: dict
        *font_size - Size of font: int
        *font_path - Path to font file: str
        *font_name - Font name in database (if have'nt path): str
    '''
    __slots__ = ['settings', 'rendered_text', 'code_name']
    def __init__(self, text: str, code_name: str, settings: dict, position=None,
                 font_size=50, font_path=None, font_name=None):
        self.settings = settings
        self.code_name = code_name
        if font_path is None:
            if font_name is None:
                font_name = 'christmas'
            font_path = self.get_font(font_name)
        super().__init__(font_path, font_size)
        self.rendered_text = self.get_text(text, position)

    def get_font(self, font_name: str) -> str:
        db_path = f'{self.settings["path"]}/assets/database/'
        database = DataBase(db_path)
        return f"{self.settings['path']}/{database.get_font(font_name)}"

    def get_text(self, text: str,
                 position: list = None):
        rendered_text = self.render(text, True, (255, 255, 255))
        if position is None:
            text_x = self.settings['window_size'][0] // 2 -\
                    rendered_text.get_width() // 2
            text_y = 20
        else:
            text_x, text_y = position[0], position[1]
        return rendered_text, (text_x, text_y)
    
    def draw(self, screen) -> None:
        screen.blit(*self.rendered_text)


class Level(Window):
    '''Level class
    
    Initilization arguments: 
        *settings - Dict with settings from class Settings: dict
        
    Methods:
        *game_cycle - Start the window(game)
        *event_handler - Work with events
        *draw - Display and draw all objects
     '''
    __slots__ = ['santa', 'all_sprites']
    def __init__(self, settings: dict):
        super().__init__(settings, mode='level')
        self.all_sprites = pygame.sprite.Group()
        self.get_sprites()      
        load = pygame.image.load
        relative_background_path = '/assets/sprites/background/background_level.png'
        background_path = f'{self.settings["path"]}{relative_background_path}'
        self.background_filler = load(background_path)
        self.santa: Player = Player([65, self.settings['window_size'][1] - 216],
                                    2, self.settings['skin'])

    def get_sprites(self):
        def get_sprite(image, position, size):
            sprite = pygame.sprite.Sprite()
            sprite.image = pygame.image.load(image)
            sprite.mask = pygame.mask.from_surface(sprite.image)
            sprite.rect = pygame.Rect((*position,), (*size,))
            self.all_sprites.add(sprite)
            return sprite
            
        def floor(position, size):
            rel_path = '/assets/sprites/background/background.png'
            floor_path = self.settings['path'] + rel_path
            return get_sprite(floor_path, position, size)
            
        def border(x1, y1, x2, y2):
            border = pygame.sprite.Sprite()
            if x1 == x2:
                border.image = pygame.Surface([1, y2 - y1])
                border.rect = pygame.Rect(x1, y1, 1, y2 - y1)
            else:
                border.image = pygame.Surface([x2 - x1, 1])
                border.rect = pygame.Rect(x1, y1, x2 - x1, 1)
            border.mask = pygame.mask.from_surface(border.image)
            self.all_sprites.add(border)
            return border
        
        def wall(position, size):
            rel_path = '/assets/sprites/wall/wall_60.png'
            wall_path = self.settings['path'] + rel_path
            return get_sprite(wall_path, position, size)

        width = self.settings['window_size'][0]
        height = self.settings['window_size'][1]
        border(0, 0, width, 0)
        border(0, height, width, height)
        border(0, 0, 0, height)
        border(width, 0, width, height)
        floor([0, 470], [10, 10])
        floor([100, -200], [0, 0])
        wall([0, 0], [10, 10])


    def game_cycle(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                running = self.event_handler(event)
            if self.santa.state['jump']:
                self.santa.jump(self.all_sprites, self.screen)
            self.clock.tick(self.fps)
            self.screen.blit(self.background_filler, [0, 0])
            self.draw()
            pygame.display.update()


    def event_handler(self, event: pygame.event) -> bool:
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()            
            if keys[pygame.K_RIGHT]:
                self.santa.move('right', self.all_sprites)
            if keys[pygame.K_LEFT]:
                self.santa.move('left', self.all_sprites)
            if keys[pygame.K_DOWN]:
                self.santa.sit()
            if keys[pygame.K_UP]:
                self.santa.stand()
        return True

    def draw(self) -> None:
        self.all_sprites.draw(self.screen)
        self.santa.gravity(self.all_sprites)
        self.santa.skin_group.draw(self.screen)

class GUI:
    '''Making work with pygame_gui easier
    
    Initilization arguments: 
        *settings - Dict with settings from class Settings: dict
        
    Methods:
        *-
    '''
    __slots__ = ['settings', 'manager']
    def __init__(self, settings: dict):
        self.settings = settings
        button_names = ['faq', 'menu', 'no', 'pause', 'play', 'replay',
                        'settings', 'shop', 'volume', 'yes']
        self.manager = pygame_gui.UIManager(self.settings['window_size'])

class Game:
    '''Main class of this programm, organanizing all windows and start it
    
    Initilization arguments: 
        *settings - Dict with settings from class Settings: dict
        *mode - Selected window
        
    Methods:
        *game_cycle - Run window
    '''
    __slots__ = ['game']

    def __init__(self, settings: dict, mode: str):
        if mode == 'level':
            self.game = Level(settings)
        elif mode == 'main_window':
            self.game = MainWindow(settings)
        elif mode == 'settings':
            self.game = SettingsWindow(settings)

    def game_cycle(self) -> None:
        self.game.game_cycle()


def get_game(mode):
    return Game(Settings(SETTINGS_FILE).settings, mode)

def run(game):
    start_mode = game.game.mode
    game.game_cycle()
    if game.game.mode != start_mode:
        new_mode = game.game.mode
        game = get_game(new_mode)
        start_mode = new_mode
        run(game)

class MainWindow(Window):
    __slots__ = ['background_filler', 'texts', 'main_text', 'buttons']

    def __init__(self, settings: dict):
        super().__init__(settings, mode='main_window')
        db_path = f'{self.settings["path"]}/assets/database/'
        database = DataBase(db_path)
        self.texts = database.get_text()
        sprites = f'{self.settings["path"]}/assets/sprites/'
        background_path = f'{sprites}/background/main_window_background.png'
        self.background_filler = pygame.image.load(background_path)
        self.main_text = Text('The Cult of Escape', 'main_text', settings)
        self.buttons = self.get_buttons()
        self.get_labels()

    def draw(self) -> None:
        self.main_text.draw(self.screen)

    def get_labels(self):
        space = self.settings['window_size'][0] // len(
            list(self.buttons.keys()))
        for button in self.buttons:
            button = self.buttons[button]
            label = Label(
                self.texts[button.code_name],
                f'{button.code_name}_label',
                self.manager,
                [1, 1],
                [1, 1],
            )
            label.connect_to_button(button, self.settings['window_size'], space)
        
    def get_buttons(self):
        images_name_list = ['faq', 'shop', 'play']
        buttons = {}
        space = self.settings['window_size'][0] // len(images_name_list)
        for index, name in enumerate(images_name_list):
            button = Button(
                '', name, self.manager,
                [5 + index * space, self.settings['window_size'][1] - 55])
            gui_path = self.settings['path'] + '/assets/sprites/icons/gui/'
            button.set_icon(gui_path+name+'.png')
            buttons[name] = button
        return buttons

    def show_faq(self):
        return Message(
            self.texts['faq_text'],
            'faq_text',
            self.manager,
            [170, 100],
            [400, 300],
            'FAQ',
        )

    def game_cycle(self) -> None:
        running = True
        faq = None
        while running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                running, faq = self.event_handler(event, running, faq)
            if faq != None and not faq.is_alive():
                faq.kill()
            self.manager.process_events(event)
            self.clock.tick(self.fps)
            self.screen.blit(self.background_filler, [0, 0])
            self.draw()
            self.gui_tools.manager.draw_ui(self.screen)
            self.gui_tools.manager.update(time_delta)
            pygame.display.update()

    def is_button_event(self, event):
        if (
            event.user_type == pygame_gui.UI_BUTTON_PRESSED
            and event.ui_element.text == ''
        ):
            for button_name in self.buttons:
                if event.ui_element == self.buttons[button_name]:
                    return True
        return False    

    def event_handler(self, event, running, faq=None):
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:                
                self.mode = 'level'
                running = False
        elif event.type == pygame.USEREVENT and self.is_button_event(event):
            button_name = event.ui_element.code_name
            if button_name == 'faq':
                faq = self.show_faq()
            elif button_name == 'play':
                self.mode = 'level'
                running = False
        return (running, faq)


game = get_game('main_window')
run(game)
pygame.quit()
