
import pygame
import pathlib
import random
import sys

SCREEN_TITLE = "Sloth"
GAME_FPS = 60
GAME_WIDTH = 1920
GAME_HEIGHT = 1080
#
# Wheels frame inner border for a 1920x1080 screen
# and a 5x4 wheelset:
#
#   x = 450, 1470
#   y = 180,  900
#
# If those are changed, the frame needs to be adjusted
SPR_WIDTH = 180
SPR_HEIGHT = 160
SPR_SPACE_X = 30
SPR_SPACE_Y = 20
# Number of Picts in a wheel
WHEEL_LENGTH = 50
# Those need to potentially be adjusted on major resolution changes
STOP_TIME = 550
SPIN_VELOCITY = 80
# How exact do we want to snap back the wheel
SNAP_SPACE = 10
SNAP_VELOCITY = -10

EV_DONE_SPINNING = pygame.USEREVENT + 1

# Win lines. Only the y coordinate is given
WINLINES = [
    # Straight lines
    [0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1],
    [2, 2, 2, 2, 2],
    [3, 3, 3, 3, 3],
    # Triangles
    [0, 1, 2, 1, 0],
    [1, 2, 3, 2, 1],
    [2, 1, 0, 1, 2],
    [3, 2, 1, 2, 3],
]

class Pict(pygame.sprite.Sprite):
    """
    Represents one image on a wheel
    """

    def __init__(self, img, init_x, init_y):
        super().__init__()
        self.image_name = img
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
        self.is_snapping_back = False
        self.stop_timer = 0.0

    def update(self, delta_time):
        # print("is_spinning:", self.is_spinning, "is_stopping:", self.is_stopping, "is_snapping_back:", self.is_snapping_back)
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
                pygame.event.post(pygame.event.Event(EV_DONE_SPINNING))

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

    def __init__(self):
        self.wheels = []
        self.pos_y = 0
        self.is_evaluating = False
        self.is_presenting_matches = False
        # This will contain the index of the winline
        # and the corresponding number of matching picts
        self.winning_lines = {}

    def insert_new_wheel(self, pos=999, spin_duration=500):
        if pos > len(self.wheels):
            pos = len(self.wheels)
        x = pos * (SPR_WIDTH + SPR_SPACE_X)
        self.wheels.insert(pos, Wheel(x, self.pos_y, WHEEL_LENGTH, spin_duration))
        self.reorder()

    def reorder(self):
        for i, wheel in enumerate(self.wheels):
            wheel.set_x(i * (SPR_WIDTH + SPR_SPACE_X))

    def get_pict_at(self, x, y):
        '''
        Return the pict at position y of wheel x,
        counted from upper left of the visible wheel area.
        Flaky.
        '''
        return self.wheels[x].spritelist[y]

    def evaluate(self):
        self.is_evaluating = True

    def update(self, delta_time):
        if self.is_evaluating:
            print("evaluating")
            for i, winline in enumerate(WINLINES):
                # Get the first pict of the winline
                match_pict = self.get_pict_at(0, winline[0])
                print("matching:", match_pict.image_name)
                print("winline:", i, winline)
                self.winning_lines[i] = 1
                # Go through the rest of the winline
                for x, y in enumerate(winline[1:]):
                    next_pict = self.get_pict_at(x+1, y)
                    print(next_pict.image_name)
                    if next_pict.image_name == match_pict.image_name:
                        print("found match:", x, y)
                        self.winning_lines[i] += 1
                    else:
                        break
            print(self.winning_lines)
            self.is_evaluating = False
            self.is_presenting_matches = True

        if self.is_presenting_matches:
            for winline, wins in self.winning_lines.items():
                if wins > 1:
                    for x in range(wins):
                        y = WINLINES[winline][x]
                        highlight_pict = self.get_pict_at(x, y)
                        pygame.draw.rect(highlight_pict.image,
                                         (255, 0, 0),
                                         [0, 0, SPR_WIDTH, SPR_HEIGHT], 3)

        for wheel in self.wheels:
            if wheel.is_spinning:
                wheel.spin_timer += delta_time
                if wheel.spin_timer >= wheel.spin_duration:
                    wheel.spin_timer = 0
                    wheel.stop()
            wheel.update(delta_time)

    def spin_all(self):
        self.is_evaluating = False
        self.is_presenting_matches = False
        for wheel in self.wheels:
            wheel.spin()

    def draw(self, surface):
        for wheel in self.wheels:
            wheel.draw(surface)

    def is_spinning(self):
        for wheel in self.wheels:
            if wheel.is_spinning:
                return True

    def force_stop_all(self):
        for wheel in self.wheels:
            if wheel.is_spinning:
                wheel.spin_timer = 0
                wheel.is_snapping_back = True
                wheel.is_stopping = False


def mainloop(screen, clock):
    delta_time = 0
    running = True
    # frame_path = pathlib.Path("images", "frame.png")
    # frame = pygame.image.load(frame_path)
    wheel_surf = pygame.Surface((1020, 720))
    wheels_x_pos = (GAME_WIDTH - ((5*SPR_WIDTH) + (4*SPR_SPACE_X))) / 2
    wm = WheelManager()
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
                    else:
                        wm.force_stop_all()
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)
            if event.type == EV_DONE_SPINNING:
                if not wm.is_spinning():
                    wm.evaluate()
        wm.update(delta_time)
        wheel_surf.fill((0,0,0))
        wm.draw(wheel_surf)
        screen.blit(wheel_surf, (wheels_x_pos, 180))
        # screen.blit(frame, (0, 0))
        pygame.display.flip()
        delta_time = clock.tick(GAME_FPS)
    pygame.quit()


if __name__ == "__main__":

    pygame.init()
    # flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
    flags = pygame.DOUBLEBUF
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), flags, vsync=True)
    clock = pygame.time.Clock()
    mainloop(screen, clock)
