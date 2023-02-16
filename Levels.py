from random import randrange

import pygame

from UI import Message
from Window import Level


class FirstLevel(Level):
    '''First level
    Have 5 thorns, 1 exit, 4 borders, 8 Bricks
    Difficulty - easy
    Initilization arguments:
        *settings - Dict with settings from class Settings: dict
        *hit_points - Count of player lifes : int
    Methods:
        *get_sprites - Load level objects
    '''
    __slots__ = []

    def __init__(self, settings: dict, hit_points: int):
        super().__init__(settings)
        self.santa.hit_points: int = hit_points
        self.get_sprites()

    def get_sprites(self) -> None:
        # Borders
        self.borders()

        # Bricks
        self.brick([200, 400])
        self.brick([300, 300])
        self.brick([200, 200])
        self.brick([400, 250])
        self.brick([432, 250])
        self.brick([464, 250])
        self.brick([464, 89])
        self.brick([550, 180])

        # Traps
        self.thorn([360, 450])
        self.thorn([300, 450])
        self.thorn([120, 450])
        self.thorn([200, 450])
        self.thorn([464, 235])

        # Exit
        self.exit([464, 68])


class SecondLevel(Level):
    '''Second level
    Have 7 thorns, 1 exit, 4 borders, 21 Bricks, 1 thorn5x, 1 vulkan
    Difficulty - normal
    Initilization arguments:
        *settings - Dict with settings from class Settings: dict
        *hit_points - Count of player lifes : int
    Methods:
        *get_sprites - Load level objects
    '''
    __slots__ = []

    def __init__(self, settings: dict, hit_points: int):
        super().__init__(settings)
        self.santa.hit_points: int = hit_points
        self.get_sprites()

    def get_sprites(self) -> None:
        # Borders
        self.borders()

        # Bricks
        self.brick([100, 100])
        self.brick([100, 200])
        self.brick([100, 300])
        self.brick([100, 400])
        self.brick([170, 360])
        self.brick([208, 172])
        self.brick([320, 120])
        self.brick([400, 200])
        self.brick([513, 230])
        self.brick([651, 300])
        self.brick([715, 205])
        for y in range(148, 468, 32):  # 10
            self.brick([240, y])

        ''' Traps '''
        # Vulkans
        self.vulkan([496, 438])
        # Thorns
        self.thorn([100, 384])
        self.thorn([116, 384])
        self.thorn([100, 284])
        self.thorn([252, 132])
        self.thorn([416, 184])
        self.thorn([635, 300], turn='left')
        self.thorn([683, 300], turn='right')
        # Thorns5x
        self.thorns5x([100, 405])

        # Exit
        self.exit([715, 189])


class ThirdLevel(Level):
    '''Third level
    Have 12 thorns, 1 exit, 4 borders, 71 Bricks, 1 vulkan, 1 chainsaw
    Difficulty - hard
    Initilization arguments:
        *settings - Dict with settings from class Settings: dict
        *hit_points - Count of player lifes : int
    Methods:
        *get_sprites - Load level objects
        *game_cycle - Game cycle with blindness effect
    '''
    __slots__ = []

    def __init__(self, settings: dict, hit_points: int):
        super().__init__(settings)
        self.santa.hit_points: int = hit_points
        self.get_sprites()

    def get_sprites(self) -> None:
        # Borders
        self.borders()

        # Bricks
        self.brick([649, 326])
        self.brick([484, 235])
        self.brick([332, 221])
        for y in range(55, 408, 32):  # 12
            self.brick([89, y])
        for i, x in enumerate(range(89, 186, 32)):  # 14
            self.brick([x, 407 - i * 10])
        for x in range(215, 248, 32):  # 2
            self.brick([x, 400])
        for y in range(80, 369, 32):  # 10
            self.brick([247, y])
        for x in range(314, 667, 32):  # 12
            self.brick([x, 400])
        for x in range(311, 600, 32):  # 10
            self.brick([x, 80])
        for y in range(80, 401, 32):  # 11
            self.brick([695, y])

        ''' Traps '''
        # Thorns
        for x in range(314, 667, 32):  # 12
            self.thorn([x, 384])
        # Chainsaws
        self.chainsaw([162, 449])
        # Vulkans
        self.vulkan([245, 440])

        # Exit
        self.exit([607, 65])

    def game_cycle(self) -> None:
        running = True
        i = 0
        while running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.manager.process_events(event)
                    running = self.event_handler(event)
                    if not running:
                        break
            if self.santa.is_collide(self.sprite_groups['exit']):
                self.mode = 'win'
                running = False
            elif self.santa.hit_points <= 0:
                self.mode = 'lose'
                running = False
            elif self.santa.is_collide(self.sprite_groups['trap']):
                self.santa.die()
            self.clock.tick(self.fps)
            self.screen.blit(self.background_filler, [0, 0])

            i += 1
            if i > 50:
                # Blindness effect
                if i > 200:
                    i = 0
                self.draw()
            else:
                self.santa.update(
                    self.sprite_groups['wall'],
                    self.all_sprites,
                    self.move_direction, self.is_jumping, self.is_sitting)
                self.reset()
                self.santa.skin_group.draw(self.screen)
                self.draw_hearts()
            self.manager.draw_ui(self.screen)
            self.manager.update(time_delta)
            pygame.display.update()


class FourthLevel(Level):
    '''Fourth level
    Have 17 thorns, 1 exit, ? bricks
    Difficulty - easy
    Initilization arguments:
        *settings - Dict with settings from class Settings: dict
        *hit_points - Count of player lifes : int
    Methods:
        *get_sprites - Load level objects
        *in_allowed_zone - Check, can player place break or not
        *event_handler - Handle events, build players bricks
    '''
    __slots__ = ['bricks']

    def __init__(self, settings: dict, hit_points: int):
        super().__init__(settings)
        self.bricks: int = 0
        self.santa.hit_points: int = hit_points
        self.get_sprites()

    def get_sprites(self) -> None:
        # Borders
        self.borders()

        # Thorns
        for x in range(100, 709, 32):  # 17
            self.thorn([x, 453])

        # Exit
        self.exit([722, 77])

    def in_allowed_zone(self, position) -> bool:
        x = position[0]
        y = position[1]
        if x in range(64) and y in range(45, 225):
            return False
        elif x in range(684, 753) and y in range(50, 96):
            return False
        return True

    def game_cycle(self) -> None:
        running = True
        while running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.manager.process_events(event)
                    running = self.event_handler(event)
                    if not running:
                        break
            if self.santa.is_collide(self.sprite_groups['exit']):
                self.mode = 'win'
                running = False
            elif self.santa.hit_points <= 0:
                self.mode = 'lose'
                running = False
            elif self.santa.is_collide(self.sprite_groups['trap']):
                self.bricks = 0
                self.santa.die()
            self.clock.tick(self.fps)
            self.screen.blit(self.background_filler, [0, 0])
            self.draw()
            self.manager.draw_ui(self.screen)
            self.manager.update(time_delta)
            pygame.display.update()

    def event_handler(self, event: pygame.event) -> bool:
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.bricks <= 3
            and self.in_allowed_zone(event.pos)
        ):
            self.brick([*event.pos])
            self.bricks += 1
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
        elif event.type == pygame.USEREVENT and self.is_button_event(event):
            button_name = event.ui_element.code_name
            if button_name == 'faq':
                Message(self.texts['build_level_tip'], 'Help',
                        self.manager, [170, 100], [400, 300], 'help_msg')
            elif button_name == 'menu':
                self.mode = 'main_window'
                return False
            elif button_name == 'replay':
                self.mode = 'replay'
                return False
        return True


class FifthLevel(Level):
    '''Fifth level
    Have 16 thorns, 1 exit, 8 bricks, 4 thorns5x, 1 box glover
    Difficulty - hard
    Initilization arguments:
        *settings - Dict with settings from class Settings: dict
        *hit_points - Count of player lifes : int
    Methods:
        *get_sprites - Load level objects
    '''
    __slots__ = []

    def __init__(self, settings: dict, hit_points: int):
        super().__init__(settings)
        self.santa.hit_points: int = hit_points
        self.get_sprites()

    def get_sprites(self) -> None:
        # Borders
        self.borders()

        # Bricks:
        self.brick([665, 238])
        self.brick([63, 284])
        self.brick([230, 342])
        self.brick([270, 166])
        self.brick([302, 198])
        self.brick([333, 230])
        self.brick([364, 261])
        self.brick([541, 127])

        ''' Traps '''
        # Thorns and Balls
        for x in range(61, 686, 16):
            self.thorn([x, 55], 'down')  # 16
            if (x - 61) % 128 == 0:
                self.ball([x, randrange(-100, -30)])  # 5
        # Box glover
        self.box_glover([650, 60])
        # Thorns5x
        self.thorns5x([192, 405])
        self.thorns5x([348, 405])
        self.thorns5x([513, 405])
        self.thorns5x([661, 405])

        # Exit
        self.exit([707, 200])