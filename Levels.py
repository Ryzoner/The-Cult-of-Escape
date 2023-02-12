from Window import Level

import pygame


class FirstLevel(Level):
    '''First level, most easiest level
    Have 4 thorns, 1 exit, 4 borders (2 floors, 2 borders)
    Initilization arguments:
        *settings - Dict with settings from class Settings: dict
        *hit_points - Count of player lifes : int
    '''
    __slots__ = []

    def __init__(self, settings: dict, hit_points: int):
        super().__init__(settings)
        self.santa.hit_points: int = hit_points
        self.get_sprites()

    def get_sprites(self) -> None:
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
    __slots__ = []

    def __init__(self, settings: dict, hit_points: int):
        super().__init__(settings)
        self.santa.hit_points: int = hit_points
        self.get_sprites()

    def get_sprites(self) -> None:
        self.borders()
        # Bricks
        self.brick([100, 100])
        self.brick([100, 200])
        self.brick([100, 300])
        self.brick([100, 400])
        self.brick([170, 360])
        for y in range(148, 468, 32):
            self.brick([240, y])
        self.brick([208, 172])
        self.brick([320, 120])
        self.brick([400, 200])
        self.brick([513, 230])
        self.brick([651, 300])
        self.brick([715, 205])
        # Traps
        self.vulkan([496, 438])
        self.thorn([100, 384])
        self.thorn([116, 384])
        self.thorn([100, 284])
        self.thorn([252, 132])
        self.thorns5x([100, 405])
        self.thorn([416, 184])
        self.thorn([635, 300], turn='left')
        self.thorn([683, 300], turn='right')
        # Exit
        self.exit([715, 189])


class ThirdLevel(Level):
    __slots__ = []

    def __init__(self, settings: dict, hit_points: int):
        super().__init__(settings)
        self.santa.hit_points: int = hit_points
        self.get_sprites()

    def get_sprites(self) -> None:
        self.borders()
        for y in range(55, 439, 32):
            self.brick([89, y])
        for i, x in enumerate(range(89, 215, 32)):
            self.brick([x, 407 - i * 10])
        for x in range(215, 279, 32):
            self.brick([x, 400])
        self.chainsaw([162, 449])
        self.vulkan([245, 440])
        for y in range(80, 369, 32):
            self.brick([247, y])
        for x in range(314, 695, 32):
            self.brick([x, 400])
        for x in range(311, 631, 32):
            self.brick([x, 80])
        for y in range(80, 401, 32):
            self.brick([695, y])
        for x in range(314, 695, 32):
            self.thorn([x, 384])
        self.brick([649, 326])
        self.brick([484, 235])
        self.brick([332, 221])
        self.exit([607, 65])

    def game_cycle(self) -> None:
        running = True
        i = 0
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
            if i > 50:
                if i > 100:
                    i = 0
                self.draw()
            else:
                self.santa.update(
                    self.sprite_groups['wall'], self.move_direction, self.is_jumping)
                self.move_direction = False
                self.is_jumping = False
                self.santa.skin_group.draw(self.screen)
                self.draw_hearts()
            i += 1
            pygame.display.update()