from Window import Level


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