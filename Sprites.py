from os import listdir
from os.path import exists
from random import choice, randrange

import pygame

from Errors import SpriteError
from Utils import Sounds


class Sprite(pygame.sprite.Sprite):
    '''Base sprite class

    Initilization arguments: 
        *position - Start position of sprite : list
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
    '''Player sprite class
    Initilization arguments: 
        *all_sprites - Group with all sprites :pygame.sprite.Group         
        *position - Start position of sprite : list
        *hit_points - Count of sprite lifes : int
        *skin_name - Opted skin : str
    Methods:
        *change_player_skin - Change player skin with selected
        *die - Teleport to spawn, decrease hp
        *get_collide_object- Return collided object
        *get_skins - Return dict with skins
        *is_collide - Check is player collided
        *move - Move player
        *update - Update player info
    '''
    
    __slots__ = ['skins', 'sounds', 'state', 'move_speed', 'particles',
                 'jump_speed', 'flip_direction']
    
    def __init__(self, position: list, hit_points: int, skin_name: str,
                 all_sprites: pygame.sprite.Group, settings: dict):
        super().__init__(position, hit_points, skin_name,
                         'assets/sprites/santa', all_sprites, settings)
        self.setup(self.get_skins()['stand'])
        self.skins: dict = self.get_skins()
        self.state: dict = {'flip': False, 'stand': False, 'sit': False}
        db_path: str = self.settings['path'] + '/assets/database/'
        self.sounds = Sounds(db_path)
        self.move_speed, self.jump_speed = 0, 0
        self.to_spawn()
        self.particles = []
        self.set_group()
        self.flip_direction = 'right'
        
    def stand(self):
        self.state['sit'] = False
        self.change_player_skin('stand')
        old_flip_dir = self.flip_direction
        self.flip_direction = 'right'
        self.flip(old_flip_dir)

    def sit(self):
        self.state['sit'] = True
        self.change_player_skin('sit')
        old_flip_dir = self.flip_direction
        self.flip_direction = 'right'
        self.flip(old_flip_dir)

    def change_player_skin(self, skin_type: str = '') -> None:
        return self.change_skin(self.get_skins()[skin_type])
    
    def flip(self, direction):
        if self.flip_direction != direction:
            self.flip_direction = direction
            self.image = pygame.transform.flip(self.image, True, False)

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
        self.state['stand'] = False

    def update(self, sprite_group, all_sprites,
               move_direction=False,
               is_jumping=False, is_sitting=False) -> None:
        for particle in self.particles:
            particle.update()
        if len(self.particles) >= 30:
            self.particles = self.particles[8:]
        if is_sitting:
            self.sit()
        if is_jumping and self.state['stand']:
            if not self.state['sit']:
                self.jump_speed = -self.settings['jump_power']
            else:
                self.stand()
        if move_direction == 'left':
            self.move_speed = -self.settings['step']
        elif move_direction == 'rigth':
            self.move_speed = self.settings['step']
        else:
            self.move_speed = 0
        if not self.state['stand']:
            self.jump_speed += self.gravity
        if self.jump_speed != 0 and self.state['stand']:
            self.sounds.play('jump')
            self.jump_skin()
        if self.move_speed != 0 and self.state['stand']:
            self.sounds.play('step')
        if self.move_speed < 0:
            self.flip('left')
        if self.move_speed > 0:
            self.flip('right')
        if self.jump_speed == 0:
            self.stand()
        self.state['stand'] = False
        self.move(sprite_group, all_sprites)
        
    def jump_skin(self):
        self.change_player_skin('jump')
        old_flip_dir = self.flip_direction
        self.flip_direction = 'right'
        self.flip(old_flip_dir)

    def move(self, sprite_group, all_sprites) -> None:
        self.rect.y += self.jump_speed
        if self.is_collide(sprite_group):
            wall = self.get_collide_object(sprite_group)
            if self.jump_speed > 0:
                if self.jump_speed != 1:
                    self.particles.append(Particles([self.rect.x, self.rect.y],
                                                    self.settings, all_sprites))
                self.rect.bottom = wall.rect.top
                self.jump_speed = 0
                self.state['stand'] = True
            if self.jump_speed < 0:
                self.rect.top = wall.rect.bottom
                self.jump_speed = 0
                self.state['stand'] = False
        elif self.jump_speed > 0:
            self.state['stand'] = False
        self.rect.x += self.move_speed
        if self.is_collide(sprite_group):
            wall = self.get_collide_object(sprite_group)
            if self.move_speed > 0:
                self.rect.right = wall.rect.left
                self.move_speed = 0
            if self.move_speed < 0:
                self.rect.left = wall.rect.right
                self.move_speed = 0

    def is_collide(self, sprite_group) -> bool:
        return any(pygame.sprite.collide_mask(self, sprite) for sprite in sprite_group)

    def get_collide_object(self, sprite_group) -> pygame.sprite.Sprite or bool:
        return next(
            (
                sprite
                for sprite in sprite_group
                if pygame.sprite.collide_mask(self, sprite)
            ),
            False,
        )
        

class Particles(pygame.sprite.Sprite):
    '''Player sprite class
    Initilization arguments: 
        *position - Start position of sprite : list
        *settings - Settings from 'Settings.setting' class: dict
        *all_sprites - Group with all sprites :pygame.sprite.Group         
    Methods:
        *get_particles - Return particles list
        *update - Update particle position
    '''
    __slots__ = ['settings', 'velocity']

    def __init__(self, position: list, settings: dict,
                 all_sprites: pygame.sprite.Group):
        super().__init__(all_sprites)
        self.settings: dict = settings
        self.image: pygame.sprite.Sprite = choice(self.get_particles())
        self.rect: pygame.Rect = self.image.get_rect()
        numbers = range(-5, 6)
        self.velocity = [choice(numbers), choice(numbers)]
        self.rect.x, self.rect.y = position

    def get_particles(self) -> list:
        load_image = pygame.image.load
        particles_rel_path = '/assets/sprites/particles/'
        particles_path: str = self.settings['path'] + particles_rel_path
        particles = [load_image(particles_path + file)
                     for file in listdir(particles_path)]
        particles.extend(
            pygame.transform.scale(choice(particles), (scale, scale))
            for scale in (2, 4, 5, 7)
        )
        return particles

    def update(self) -> None:
        self.velocity[1] += 1
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(
            (0, 0, self.settings['window_size'][0],
             self.settings['window_size'][1])):
            self.kill()
            

class Ball(pygame.sprite.Sprite):
    def __init__(self, position: list, settings: dict):
        super().__init__()
        self.settings: dict = settings
        self.image: pygame.sprite.Sprite = self.get_image()
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

    def get_image(self) -> list:
        load_image = pygame.image.load
        image_rel_path = '/assets/sprites/traps/ball/ball_0.png'
        image_path: str = self.settings['path'] + image_rel_path
        return load_image(image_path)

    def update(self) -> None:
        window_size = self.settings['window_size']
        self.rect.y += 15
        if not self.rect.colliderect((
                0, 0, window_size[0], window_size[1] + 400)):
            self.rect.y = randrange(-400, -30)
