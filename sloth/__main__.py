
import pygame
import pathlib
import random
import sys

SCREEN_TITLE = "Sloth"
SPR_WIDTH = 60
SPR_HEIGHT = 60
SPR_SPACE_X = 20
SPR_SPACE_Y = 15
# number of Picts in a wheel
WHEEL_LENGTH = 50
STOP_TIME = 550
SPIN_VELOCITY = 50
# how exact do we want to snap back the wheel
SNAP_SPACE = 3
SNAP_VELOCITY = -3
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
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.is_spinning = False
        self.is_stopping = False
        self.is_snapping_back = False
        self.stop_timer = 0.0
        self.velocity = 0.0
        self.spin_timer = 0
        self.spin_duration = spin_duration
        self.spritelist = []

        symbol_path = pathlib.Path("images", "pictures")
        symbols = list(symbol_path.glob("*.png"))
        for i, sym in enumerate(random.choices(symbols, k=num)):
            y = self.pos_y + i * SPR_HEIGHT + i * SPR_SPACE_Y
            p = Pict(sym, self.pos_x, y)
            self.spritelist.append(p)
            self.add(p)

    def set_velocity(self, velocity):
        self.velocity = velocity

    def get_velocity(self) -> float:
        return self.velocity

    def spin(self):
        self.stop_timer = 0.0
        self.is_spinning = True
        self.set_velocity(SPIN_VELOCITY)

    def stop(self):
        self.is_stopping = True
        self.stop_timer = 0.0

    def update(self, delta_time):
        if self.is_stopping and self.is_spinning and not self.is_snapping_back:
            self.stop_timer += delta_time
            if self.stop_timer >= STOP_TIME:
                self.is_stopping = False
                self.set_velocity(0)
                self.is_snapping_back = True
            else:
                # Soft stop
                cur_v = self.get_velocity()
                steps = STOP_TIME / delta_time
                self.set_velocity(cur_v - SPIN_VELOCITY / steps)

        if self.is_spinning and not self.is_stopping and self.is_snapping_back:
            top_y = self.spritelist[0].rect.y
            # Slowly snap back to a nice position
            if top_y > SNAP_SPACE:
                snap_gap = top_y - SNAP_SPACE
                self.set_velocity(max(SNAP_VELOCITY, - snap_gap/2))
            else:
                self.set_velocity(0)
                self.is_snapping_back = False
                self.is_spinning = False

        for spr in self.sprites():
            spr.update(self.get_velocity())

        # If there is enough space on the top, move the last element up
        # This way the wheel appears circular.
        if self.spritelist[0].rect.y >= SPR_HEIGHT + SPR_SPACE_Y: 
            last_sprite = self.spritelist[-1]
            last_sprite.rect.y = self.spritelist[0].rect.y - (SPR_HEIGHT + SPR_SPACE_Y)
            self.spritelist.insert(0, last_sprite)
            self.spritelist.pop()


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
        self.pos_y = 0

    def insert_new_wheel(self, pos=999, spin_duration=500):
        if pos > len(self.wheels):
            pos = len(self.wheels)
        x = self.pos_x + pos * (SPR_WIDTH + SPR_SPACE_X)
        self.wheels.insert(pos, Wheel(x, self.pos_y, WHEEL_LENGTH, spin_duration))
        self.reorder()

    def reorder(self):
        for i, wheel in enumerate(self.wheels):
            wheel.set_x(self.pos_x + i * (SPR_WIDTH + SPR_SPACE_X))

    def update(self, delta_time):
        for wheel in self.wheels:
            wheel.update(delta_time)

    def spin_all(self):
        for wheel in self.wheels:
            wheel.spin()

    def draw(self, surface):
        for wheel in self.wheels:
            wheel.draw(surface)

    def is_spinning(self):
        for wheel in self.wheels:
            if wheel.is_spinning:
                return True


def mainloop(screen, clock):
    delta_time = 0
    running = True
    # frame_path = pathlib.Path("images", "frame.png")
    # frame = pygame.image.load(frame_path)
    wheels_x_pos = (800 - ((5*SPR_WIDTH) + (4*SPR_SPACE_X))) / 2
    wm = WheelManager(wheels_x_pos)
    wm.insert_new_wheel(spin_duration=1000)
    wm.insert_new_wheel(spin_duration=1300)
    wm.insert_new_wheel(spin_duration=1600)
    wm.insert_new_wheel(spin_duration=1900)
    wm.insert_new_wheel(spin_duration=2200)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not wm.is_spinning():
                        wm.spin_all()
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)
        screen.fill((0,0,0))
        for wheel in wm.wheels:
            if wheel.is_spinning:
                wheel.spin_timer += delta_time
                if wheel.spin_timer >= wheel.spin_duration:
                    wheel.spin_timer = 0
                    wheel.stop()
        wm.update(delta_time)
        wm.draw(screen)
        # screen.blit(frame, (0, 0))
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
