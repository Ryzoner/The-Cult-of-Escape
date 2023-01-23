from os.path import exists

from Utils import Sounds

from Errors import SpriteError

import pygame


class Sprite(pygame.sprite.Sprite):
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
    __slots__ = ['start_position', 'hit_points', 'settings',
                 'skin_group', 'width', 'height', 'folder_path', 'skin_name']

    def __init__(self, position: list, hit_points: int, skin_name: str,
                 folder_path: str, all_sprites, settings):
        super().__init__(all_sprites)
        self.start_position: list = position
        self.hit_points: int = hit_points
        self.skin_name: str = skin_name
        self.folder_path: str = folder_path
        self.settings: dict = settings
        self.gravity = self.settings['gravity']

    def setup(self, full_file_path: str) -> None:
        self.set_skin(full_file_path)
        self.width: int = self.image.get_width()
        self.height: int = self.image.get_height()

    def set_group(self) -> None:
        self.skin_group = pygame.sprite.Group()
        self.skin_group.add(self)

    def to_spawn(self) -> None:
        self.teleport(self.start_position)

    def teleport(self, position: list) -> None:
        self.rect.x, self.rect.y = position

    def full_file_path(self, skin_path: str) -> str:
        game_path: str = self.settings['path']
        sprite_folder = f'{game_path}/{self.folder_path}'
        return f'{sprite_folder}/{self.skin_name}/{skin_path}'

    def set_skin(self, skin_path: str) -> None:
        full_skin_path = self.full_file_path(skin_path)
        if not exists(full_skin_path):
            raise SpriteError
        self.image = pygame.image.load(full_skin_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.start_position
        self.mask = pygame.mask.from_surface(self.image)

    def change_skin(self, skin_path: str) -> pygame.sprite.Sprite:
        full_skin_path = self.full_file_path(skin_path)
        if not exists(full_skin_path):
            raise SpriteError
        current_position = (self.rect.x, self.rect.y)
        self.image = pygame.image.load(full_skin_path)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = current_position

    def is_in_window(self, position: list) -> bool:
        x: int = position[0]
        if x not in range(self.settings['window_size'][0] + self.width):
            return False
        y: int = position[1]
        return y in range(self.settings['window_size'][1] + self.height)


class Player(Sprite):
    def __init__(self, position: list, hit_points: int, skin_name: str,
                 all_sprites, settings):
        super().__init__(position, hit_points, skin_name,
                         'assets/sprites/santa', all_sprites, settings)
        self.setup(self.get_skins()['stand'])
        self.skins: dict = self.get_skins()
        self.state: dict = {'flip': False, 'stand': False}
        db_path: str = self.settings['path'] + '/assets/database/'
        self.sounds = Sounds(db_path)
        self.move_speed = 0
        self.jump_speed = 0
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

    def update(self, sprite_group, move_direction=False,
               is_jumping=False) -> None:
        if is_jumping and self.state['stand']:
            self.jump_speed = -self.settings['jump_power']
        if move_direction == 'left':
            self.move_speed = -self.settings['step']
        elif move_direction == 'rigth':
            self.move_speed = self.settings['step']
        else:
            self.move_speed = 0
        if not self.state['stand']:
            self.jump_speed += self.settings['gravity']
        self.move(sprite_group)

    def move(self, sprite_group) -> None:
        self.state['stand'] = False
        self.rect.y += self.jump_speed
        self.rect.x += self.move_speed
        if self.is_collide(sprite_group):
            if self.move_speed > 0:
                self.rect.x -= self.move_speed
            if self.move_speed < 0:
                self.rect.x += self.move_speed
            if self.is_collide(sprite_group):
                self.rect.x -= self.move_speed * 2
            if self.jump_speed > 0:
                self.state['stand'] = True
                self.rect.y -= self.jump_speed
                self.jump_speed = 0
            if self.jump_speed < 0:
                self.rect.y += self.jump_speed
                self.jump_speed = 0
            if self.is_collide(sprite_group):
                self.rect.y += 3

    def is_collide(self, sprite_group) -> bool:
        return any(pygame.sprite.collide_mask(self, sprite) for sprite in sprite_group)