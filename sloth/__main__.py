
import pygame
import pathlib
import random

SCREEN_TITLE = "Sloth"
SPR_WIDTH = 120
SPR_HEIGHT = 120
SPR_SPACE_Y = 15
# number of Picts in a wheel
WHEEL_LENGTH = 6
# Seconds
SPIN_TIME = 1
STOP_TIME = 0.2
SPIN_VELOCITY = 2
GAME_FPS = 60
GAME_RES = (0, 0)


class Pict(pygame.sprite.Sprite):
    """
    Represents one image on a wheel
    """

    def __init__(self, img, init_x, init_y):
        super().__init__()
        # self.image = pygame.Surface([SPR_WIDTH, SPR_HEIGHT])
        self.image = pygame.image.load(img)
        self.image = pygame.transform.scale(self.image, (SPR_WIDTH, SPR_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = init_x
        self.rect.y = init_y

    def update(self):
        if self.rect.y < SPR_HEIGHT / 2:
            # this does not work, because we do not know at which
            # position the wheel has stopped.
            self.rect.y = WHEEL_LENGTH * (SPR_HEIGHT + SPR_SPACE_Y)


class Wheel(pygame.sprite.Group):
    """
    Represents one wheel of slot machine
    """

    def __init__(self, pos_x, pos_y, num):
        super().__init__()
        self.pos_y = pos_y
        self.is_spinning = False
        self.is_stopping = False
        self.stop_timer = 0.0
        self.velocity = 0.0
        symbol_path = pathlib.Path("images", "pictures")
        symbols = list(symbol_path.glob("*.png"))
        random.shuffle(symbols)
        for i, sym in enumerate(symbols[0:num]):
            y = self.pos_y + i * SPR_HEIGHT + i * SPR_SPACE_Y
            p = Pict(sym, pos_x, y)
            # p.scale = SPR_WIDTH / p.width
            self.add(p)

    def set_velocity(self, velocity):
        self.velocity = velocity
        for spr in self.sprites():
            spr.rect.y = velocity

    def get_velocity(self) -> float:
        return self.velocity

    def spin(self):
        self.is_spinning = True
        self.set_velocity(SPIN_VELOCITY)

    def stop(self):
        self.is_stopping = True
        self.stop_timer = 0.0

    def update(self, delta_time):
        if self.is_stopping and self.is_spinning:
            self.stop_timer += delta_time
            if self.stop_timer >= STOP_TIME:
                self.is_spinning = False
                self.is_stopping = False
                self.set_velocity(0)
            else:
                cur_v = self.get_velocity()
                steps = STOP_TIME / delta_time
                self.set_velocity(cur_v - SPIN_VELOCITY / steps)
        for spr in self.sprites():
            spr.update()

    # def draw(self):
    #     super().draw()
    #     for spr in self.sprites():
    #         # spr.draw()

def mainloop(screen, clock):
    delta_time = 0
    running = True
    spin_timer = 0
    # x = 0
    # inc = 10
    wheel1 = Wheel(50, 50, 12)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    wheel1.spin()
        screen.fill((0,0,0))
        # x = (x + inc) % screen.get_width()
        # pygame.draw.line(screen, (255, 255, 255), (x, 0), (x, screen.get_height()), 1)
        if wheel1.is_spinning:
            spin_timer += delta_time
            if spin_timer >= SPIN_TIME:
                spin_timer = 0
                wheel1.stop()
        wheel1.update(delta_time)
        wheel1.draw(screen)
        pygame.display.flip()
        delta_time = clock.tick(GAME_FPS)
    pygame.quit()


# class Sloth(arcade.Window):
#     """
#     Sloth Slot Machine Game
#     """

#     def __init__(self, w, h, t):
#         super().__init__(w, h, t, vsync=True)
#         self.antialiasing = True
#         self.samples = 16
#         arcade.set_background_color(colors.WHITE)
#         self.spin_timer = 0


    def on_update(self, delta_time: float):
        self.strip1.on_update(delta_time)


if __name__ == "__main__":

    pygame.init()
    flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
    screen = pygame.display.set_mode(GAME_RES, flags, vsync=1)
    clock = pygame.time.Clock()
    mainloop(screen, clock)
