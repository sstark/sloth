

class Animation:

    def __init__(self):
        # velocity in pixels per frame
        self.velocity: int = 0

    def get_velocity(self):
        return self.velocity

    def set_velocity(self, v):
        # Should take a function that can be used to modify the velocity over
        # time.
        self.velocity = v


class GameRegime:
    """

    This class holds the game state.

      - Organize all animations and allowed transitions between animations
      - Provide independent timers for animations
      - Must be hooked into the game main loop

    """

    def __init__(self):
        self.animations: list[Animation] = []
