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
        #Bricks
        self.brick([200, 400])
        self.brick([300, 300])
        self.brick([200, 200])
        self.brick([400, 250])
        self.brick([432, 250])
        self.brick([464, 250])
        self.brick([464, 89])
        self.brick([550, 180])
        #Traps
        self.thorn([360, 450])
        self.thorn([300, 450])
        self.thorn([120, 450])
        self.thorn([200, 450])
        # Exit
        self.exit([468, 68])