import pygame
from os.path import exists, dirname, abspath
from configparser import ConfigParser

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()


class Santa:
    

    def __init__(self, hp, position, skin_name="red"):
        self.hp = hp
        self.is_sit = False
        self.flipped = 0
        self.is_jump = False
        self.position = position
        self.skin_name = skin_name
        self.settings = Settings("settings.ini").settings
        music_path = self.settings['path'] + '/assets/audio'
        self.sounds = {'move': pygame.mixer.Sound(f'{music_path}/step.ogg'),
                       "die": pygame.mixer.Sound(f'{music_path}/die.mp3')}
        self.skin = self.set_skin(skin_name)
        x, y = position
        self.skin.rect.x = x
        self.skin.rect.y = y - 32
        self.set_group()
        
        
    def set_group(self):
        self.skin_group = pygame.sprite.Group()
        self.skin_group.add(self.skin)

    def set_skin(self, skin_name: str, skin_type: str = ''):
        game_path = self.settings["path"]
        skin_file_name = f"santa_{skin_name}_skin.png"
        skin_name = skin_name.rstrip(skin_type + "_")
        skin_path = f"{game_path}/assets/sprites/santa/{skin_name}/{skin_file_name}"
        if not exists(skin_path):
            return self.set_skin("red")
        sprite = pygame.sprite.Sprite()
        sprite.image = pygame.image.load(skin_path)
        sprite.image.set_colorkey(pygame.Color("white"))
        sprite.image = pygame.transform.scale(sprite.image, (64, 64))
        sprite.rect = sprite.image.get_rect()
        return sprite

    def die(self):
        self.hp -= 1
        self.to_spawn()
        
    def to_spawn(self):
        x, y = self.position
        self.skin.rect.x = x
        self.skin.rect.y = y
        
    def is_in_window(self, position: list):
        if position[0] not in range(self.settings['window_size'][0] + 32):
            return False
        elif position[1] not in range(self.settings['window_size'][1] + 32):
            return False
        return True
    
    def flip(self):
         self.skin.image = pygame.transform.flip(self.skin.image, True, False)
         self.flipped = not self.flipped
        
    def sit(self):
        if self.is_sit or self.is_jump:
            return
        old_position = [self.skin.rect.x, self,skin.rect.y]
        self.skin = self.set_skin(self.skin_name + '_sit', "sit")
        if self.flipped:
            self.flip()
        self.skin.rect.x = old_position[0]
        self.skin.rect.y = old_position[1]
        self.set_group()
        self.is_sit = True
        
    def stand(self):
        if not self.is_sit or self.is_jump:
            return
        old_position = [self.skin.rect.x, self,skin.rect.y]
        self.skin = self.set_skin(self.skin_name)
        self.skin.rect.x = old_position[0]
        self.skin.rect.y = old_position[1]
        self.set_group()
        self.is_sit = False
        
    def jump(self):
        if self.is_jump:
            return
        if self.is_sit:
            return self.stand()
        else:
            old_position = [self.skin.rect.x, self,skin.rect.y]
            self.skin = self.set_skin(self.skin_name + '_jump', 'jump')
            self.skin.rect.x = old_position[0]
            self.skin.rect.y = old_position[1]
            self.set_group()
            
    def move(self, direction: str):
        if self.is_sit:
            return
        if direction = "right":
            if self.skin.rect.x + 1 not in range(
                0, self.settings['window_size'][0] - 32):
                return
            self.skin.rect.x += 1
            if self.flipped:
                self.flip()
        elif direction = "left":
            if self.skin.rect.x - 1 not in range(
                0, self.settings['window_size'][0] - 32):
                return
            self.skin.rect.x -= 1
            if not self.flipped:
                self.flip()
        self.sounds['move'].play()

class Level:
    __slots__ = ["name", "difficulty"]

    def __init__(self, name: str, difficulty: str):
        self.name = name
        self.difficulty = difficulty


class StartGame:
    __slots__ = ["running", "clock", "settings", "screen", "santa"]

    def __init__(self, settings: dict):
        self.running = True
        self.clock = pygame.time.Clock()
        self.settings = settings

    def get_screen(self, window_size: list):
        screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Christmas Adventures")
        return screen

    def start(self):
        self.santa = Santa(2, [0, 100 - 32], "thief")
        self.screen = self.get_screen(self.settings["window_size"])
        fps = self.settings["fps"]
        background_color = self.settings["background_color"]
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.santa.move("right")
            elif keys[pygame.K_LEFT]:
                self.santa.move("left")
            elif keys[pygame.K_UP]:
                self.santa.jump()
            elif keys[pygame.K_DOWN]:
                self.santa.sit()
            self.clock.tick(fps)
            self.screen.fill(background_color)
            self.run_main_window()
            pygame.display.update()
        pygame.quit()
        exit()

    def run_main_window(self):
        self.santa.skin_group.draw(self.screen)


class Settings:
    def __init__(self, settings_file_name: str):
        self.settings_path = f"./{settings_file_name}"
        self.settings_parser = ConfigParser()
        self.all_settings()

    def all_settings(self):
        self.settings_parser.read(self.settings_path, encoding="utf-8")
        dirty_settings = self.settings_parser["ChristmasAdventures"]
        fps = int(dirty_settings["fps"])
        backround_color = dirty_settings["backround_color"]
        window_size = list(map(int, dirty_settings["window_size"].split("x")))
        path = dirname(abspath(__file__))
        self.settings = {
            "fps": fps,
            "path": path,
            "background_color": backround_color,
            "window_size": window_size,
        }


game = StartGame(Settings("settings.ini").settings)
game.start()
