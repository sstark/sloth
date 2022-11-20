
import pygame
import pathlib
import random

SCREEN_TITLE = "Sloth"
SPR_WIDTH = 60
SPR_HEIGHT = 60
SPR_SPACE_X = 20
SPR_SPACE_Y = 15
# number of Picts in a wheel
WHEEL_LENGTH = 8
STOP_TIME = 550
SPIN_VELOCITY = 5
GAME_FPS = 60
GAME_RES = (800, 600)


class Pict(pygame.sprite.Sprite):
    """
    Represents one image on a wheel
    """

    def __init__(self, img, init_x, init_y):
        super().__init__()
        self.image = pygame.image.load(img)
        self.image = pygame.transform.scale(self.image, (SPR_WIDTH, SPR_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = init_x
        self.rect.y = init_y

    def update(self, velocity):
        self.rect.y += velocity
        return self.rect


class Wheel(pygame.sprite.Group):
    """
    Represents one wheel of slot machine
    """

    def __init__(self, pos_x, pos_y, num, spin_duration):
        super().__init__()
        self.pos_y = pos_y
        self.is_spinning = False
        self.is_stopping = False
        self.stop_timer = 0.0
        self.velocity = 0.0
        self.height = 600
        self.spin_timer = 0
        self.spin_duration = spin_duration
        self.spritelist = []

        symbol_path = pathlib.Path("images", "pictures")
        symbols = list(symbol_path.glob("*.png"))
        for i, sym in enumerate(random.choices(symbols, k=num)):
            y = self.pos_y + i * SPR_HEIGHT + i * SPR_SPACE_Y
            p = Pict(sym, pos_x, y)
            # p.scale = SPR_WIDTH / p.width
            self.spritelist.append(p)
            self.add(p)

    def set_velocity(self, velocity):
        self.velocity = velocity

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
            spr_pos = spr.update(self.get_velocity())
            if spr_pos.y > 600-30:
                top_y = self.spritelist[0].rect.y
                new_y = top_y - (SPR_HEIGHT + SPR_SPACE_Y)
                print("wrap:", spr_pos, top_y, new_y, len(self.spritelist))
                spr.rect.y = new_y
                self.spritelist.pop()
                self.spritelist.insert(0, spr)


    def set_x(self, x):
        for spr in self.sprites():
            spr.rect.x = x


class WheelManager():
    """
    A group of wheels
    """

    def __init__(self, pos_x):
        self.wheels = []
        self.pos_x = pos_x
        w_pixel_length = WHEEL_LENGTH * (SPR_HEIGHT + SPR_SPACE_Y)
        self.pos_y = - w_pixel_length + 600

    def insert_new_wheel(self, pos=999, spin_duration=500):
        if pos > len(self.wheels):
            pos = len(self.wheels)
        x = self.pos_x + (pos+1) * (SPR_WIDTH + SPR_SPACE_X)
        self.wheels.insert(pos, Wheel(x, self.pos_y, WHEEL_LENGTH, spin_duration))
        self.reorder()

    def reorder(self):
        for i, wheel in enumerate(self.wheels):
            wheel.set_x(self.pos_x + (i+1) * (SPR_WIDTH + SPR_SPACE_X))

    def update(self, delta_time):
        for wheel in self.wheels:
            wheel.update(delta_time)

    def spin_all(self):
        for wheel in self.wheels:
            wheel.spin()

    def draw(self, surface):
        for wheel in self.wheels:
            wheel.draw(surface)


def mainloop(screen, clock):
    delta_time = 0
    running = True
    wm = WheelManager(200)
    wm.insert_new_wheel(spin_duration=1500)
    wm.insert_new_wheel(spin_duration=1900)
    wm.insert_new_wheel(spin_duration=2300)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    wm.spin_all()
        screen.fill((0,0,0))
        for wheel in wm.wheels:
            if wheel.is_spinning:
                wheel.spin_timer += delta_time
                if wheel.spin_timer >= wheel.spin_duration:
                    wheel.spin_timer = 0
                    wheel.stop()
        wm.update(delta_time)
        wm.draw(screen)
        pygame.display.flip()
        delta_time = clock.tick(GAME_FPS)
    pygame.quit()


if __name__ == "__main__":

    pygame.init()
    # flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
    flags = pygame.DOUBLEBUF
    screen = pygame.display.set_mode(GAME_RES, flags, vsync=1)
    clock = pygame.time.Clock()
    mainloop(screen, clock)
