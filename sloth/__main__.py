
import pygame
import pathlib
import random

SCREEN_TITLE = "Sloth"
SPR_WIDTH = 60
SPR_HEIGHT = 60
SPR_SPACE_Y = 15
# number of Picts in a wheel
WHEEL_LENGTH = 50
# Seconds
SPIN_TIME = 500
STOP_TIME = 120
SPIN_VELOCITY = 50
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
        self.height = 600

        symbol_path = pathlib.Path("images", "pictures")
        symbols = list(symbol_path.glob("*.png"))
        for i, sym in enumerate(random.choices(symbols, k=num)):
            y = self.pos_y + i * SPR_HEIGHT + i * SPR_SPACE_Y
            p = Pict(sym, pos_x, y)
            # p.scale = SPR_WIDTH / p.width
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
            spr.update(self.get_velocity())


def mainloop(screen, clock):
    delta_time = 0
    running = True
    spin_timer1 = 0
    spin_timer2 = 0
    spin_timer3 = 0
    # initial y position of the wheel
    w_pixel_length = WHEEL_LENGTH * (SPR_HEIGHT + SPR_SPACE_Y)
    w_y_pos = - w_pixel_length + 600
    wheel1 = Wheel(300, w_y_pos, WHEEL_LENGTH)
    wheel2 = Wheel(300+SPR_WIDTH, w_y_pos, WHEEL_LENGTH)
    wheel3 = Wheel(300+2*SPR_WIDTH, w_y_pos, WHEEL_LENGTH)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    wheel1.spin()
                    wheel2.spin()
                    wheel3.spin()
        screen.fill((0,0,0))
        if wheel1.is_spinning:
            spin_timer1 += delta_time
            if spin_timer1 >= SPIN_TIME:
                spin_timer1 = 0
                wheel1.stop()
        if wheel2.is_spinning:
            spin_timer2 += delta_time
            if spin_timer2 >= SPIN_TIME:
                spin_timer2 = 0
                wheel2.stop()
        if wheel3.is_spinning:
            spin_timer3 += delta_time
            if spin_timer3 >= SPIN_TIME:
                spin_timer3 = 0
                wheel3.stop()
        wheel1.update(delta_time)
        wheel2.update(delta_time)
        wheel3.update(delta_time)
        wheel1.draw(screen)
        wheel2.draw(screen)
        wheel3.draw(screen)
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
