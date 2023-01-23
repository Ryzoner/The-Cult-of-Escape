from Windows import Level


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
        width: int = self.settings['window_size'][0]
        height: int = self.settings['window_size'][1]
        # Borders
        self.border(0, 0, 0, height)
        self.border(0, 0, 10, 10)
        self.floor([360, 300], [0, 0])
        self.floor([0, 470], [10, 10])
        # Traps
        self.thorn([360, 450], [10, 10])
        self.thorn([300, 450], [10, 10])
        self.thorn([120, 450], [10, 10])
        self.thorn([200, 450], [10, 10])
        # Exit
        self.exit([width - 60, height - 60], [10, 10])