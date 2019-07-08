from action import Action


class Agent:

    __slots__ = '_model'

    def __init__(self):
        pass

    def predict(self, state):
        return Action.random()
