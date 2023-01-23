import pygame
import pygame_gui
from Utils import DataBase, Sounds
from UI import Text, Button, Label, Message
from Sprites import Player


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
                 'database']

    def __init__(self, settings: dict, mode: str):
        pygame.event.set_allowed(
            [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.KEYUP,
             pygame.USEREVENT, pygame.MOUSEBUTTONUP])
        pygame.key.set_repeat(1, 100)
        self.settings: dict = settings
        self.manager = pygame_gui.UIManager(self.settings['window_size'])
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
            'Christmas Adventures', self.settings['window_size'])

    def get_screen(self, title: str, window_size: list) -> pygame.Surface:
        flags = pygame.DOUBLEBUF
        screen: pygame.Surface = pygame.display.set_mode(window_size, flags)
        screen.set_alpha(None)
        pygame.display.set_caption(title)
        return screen


class Level(Window):
    '''Base Level class
    Initilization arguments: 
        *settings - Dict with settings from class Settings: dict
    Methods:
        *game_cycle - Start the window(game)
        *event_handler - Work with events
        *draw - Display and draw all objects
     '''
    __slots__ = ['santa', 'all_sprites', 'exit_sprites',
                 'gui_sprites', 'wall_sprites', 'sprite_groups', 'trap_sprites',
                 'move_direction', 'is_jumping', 'is_sitting']

    def __init__(self, settings: dict):
        super().__init__(settings, mode='level')
        self.move_direction = False
        self.is_jumping = False
        self.is_sitting = False
        self.all_sprites = pygame.sprite.Group()
        self.exit_sprites = pygame.sprite.Group()
        self.gui_sprites = pygame.sprite.Group()
        self.wall_sprites = pygame.sprite.Group()
        self.trap_sprites = pygame.sprite.Group()
        self.sprite_groups = {'all': self.all_sprites,
                              'exit': self.exit_sprites,
                              'gui': self.gui_sprites,
                              'wall': self.wall_sprites,
                              'trap': self.trap_sprites}
        load = pygame.image.load
        relative_background_path = '/assets/sprites/background/background_level.png'
        background_path = f'{self.settings["path"]}{relative_background_path}'
        self.background_filler = load(background_path)
        self.santa: Player = Player([65, self.settings['window_size'][1] - 216],
                                    2, self.settings['skin'], self.all_sprites,
                                    self.settings)

    def get_sprite(self, image, position,
                   size=[10, 10], sprite_groups=[]) -> pygame.sprite.Sprite:
        sprite = pygame.sprite.Sprite()
        sprite.image = pygame.image.load(image)
        sprite.mask = pygame.mask.from_surface(sprite.image)
        sprite.rect = pygame.Rect((*position,), (*size,))
        self.all_sprites.add(sprite)
        if sprite_groups != []:
            for sprite_group in sprite_groups:
                sprite_group.add(sprite)
        return sprite

    def floor(self, position, size=[10, 10]) -> pygame.sprite.Sprite:
        sprite_groups = [self.wall_sprites]
        rel_path = '/assets/sprites/wall/wall_800x60.png'
        floor_path = self.settings['path'] + rel_path
        return self.get_sprite(floor_path, position, size, sprite_groups)

    def border(self, x1, y1, x2, y2) -> pygame.sprite.Sprite:
        if x1 == x2:
            return self.floor([x1, y1], [1, y2 - y1])
        else:
            return self.wall([x1, y1], [x2 - x1, 1])

    def wall(self, position, size=[10, 10]) -> pygame.sprite.Sprite:
        sprite_groups = [self.wall_sprites]
        rel_path = '/assets/sprites/wall/wall_60x595.png'
        wall_path = self.settings['path'] + rel_path
        return self.get_sprite(wall_path, position, size, sprite_groups)

    def exit(self, position, size) -> pygame.sprite.Sprite:
        sprite_groups = [self.exit_sprites]
        rel_path = '/assets/sprites/icons/reward/trophey.png'
        trophey_path = self.settings['path'] + rel_path
        return self.get_sprite(trophey_path, position, size, sprite_groups)

    def thorn(self, position, size) -> pygame.sprite.Sprite:
        sprite_groups = [self.trap_sprites]
        rel_path = '/assets/sprites/traps/thorn.png'
        thorn_path = self.settings['path'] + rel_path
        return self.get_sprite(thorn_path, position, size, sprite_groups)

    def game_cycle(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                running = self.event_handler(event)
            if self.santa.is_collide(self.sprite_groups['exit']):
                self.mode = 'win'
                running = False
            if self.santa.is_collide(self.sprite_groups['trap']):
                self.santa.die()
            if self.santa.hit_points <= 0:
                self.mode = 'lose'
                running = False
            self.clock.tick(self.fps)
            self.screen.blit(self.background_filler, [0, 0])
            self.draw()
            pygame.display.update()

    def event_handler(self, event: pygame.event) -> bool:
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.move_direction = 'rigth'
            if keys[pygame.K_LEFT]:
                self.move_direction = 'left'
            if keys[pygame.K_DOWN]:
                self.is_sitting = True
            if keys[pygame.K_UP]:
                self.is_jumping = True
        return True

    def draw(self) -> None:
        self.all_sprites.draw(self.screen)
        self.santa.update(
            self.sprite_groups['wall'], self.move_direction, self.is_jumping)
        self.move_direction = False
        self.is_jumping = False
        self.santa.skin_group.draw(self.screen)


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
        self.main_text = Text('Christmas Adventures', 'main_text', settings)
        self.buttons = self.get_buttons()
        self.get_labels()

    def draw(self) -> None:
        self.main_text.draw(self.screen)

    def get_labels(self) -> None:
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
            label.connect_to_button(
                button, self.settings['window_size'], space)

    def get_buttons(self) -> dict:
        images_name_list = ['faq', 'shop', 'play']
        buttons = {}
        space = self.settings['window_size'][0] // len(images_name_list)
        for index, name in enumerate(images_name_list):
            button = Button(
                '', name, self.manager,
                [5 + index * space, self.settings['window_size'][1] - 55])
            gui_path = self.settings['path'] + '/assets/sprites/icons/gui/'
            button.set_icon(gui_path + name + '.png')
            buttons[name] = button
        return buttons

    def show_faq(self) -> Message:
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
            self.manager.draw_ui(self.screen)
            self.manager.update(time_delta)
            pygame.display.update()

    def is_button_event(self, event) -> bool:
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

