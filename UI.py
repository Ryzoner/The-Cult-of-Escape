# -*- coding: utf-8 -*-

from Utils import DataBase

import pygame_gui
import pygame


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
        
    Methods:
        *draw - Draw itself on screen
        *get_font - Load font from database
        *get_text - Load rendered text
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
                 position: list = None) -> (pygame.font.Font.render, (int, int)):
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
        self.rect.x = position[0]
        self.rect.y = position[1]

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
                 position: list, size: list = [50, 50]):
        relative_rect = self.get_rect((*position,), (*size,))
        super().__init__(relative_rect=relative_rect, text=text,
                         manager=manager)
        self.code_name = code_name

    def load_icon(self, icon_path) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load(icon_path), [50, 50])

    def set_icon(self, icon_path) -> None:
        icon_extension = '.' + icon_path.split('.')[-1]
        hovered_icon_path = '.'.join(icon_path.split(icon_extension)[:-1]) +\
            '_pressed' + icon_extension
        icon = self.load_icon(icon_path)
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
