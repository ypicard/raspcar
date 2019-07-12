from enum import Enum
import random


class Action(Enum):
    TURN_RIGHT = 1
    TURN_LEFT = 2
    GO_STRAIGHT = 0

    @staticmethod
    def random():
        return random.choice(list(Action))
