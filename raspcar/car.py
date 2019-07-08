from time import sleep
import cv2
import logging
import io
import my_radar
import my_camera
from agent import Agent


class Car():

    __slots__ = '_camera', '_radars', '_agent', '_state'

    def __init__(self):
        logging.debug("Car.__init__")
        self._camera = my_camera.MyCamera()
        self._radars = [my_radar.MyRadar(18, 24)]
        self._agent = Agent()

    def update(self):
        logging.debug('Car.update')
        state = self.state()
        logging.debug(f'state shape={len(state)}')
        action = self._agent.predict(state)
        logging.debug(f'action={action}')
        self._act(action)
        self._state = state

    def _act(self, action):
        pass

    def state(self):
        state = []
        # radar states
        for radar in self._radars:
            state.append(radar.distance())
        # video state
        state += self._camera.lanes()

        return state


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting script...")
    car = Car()
    sleep(2)
    while True:
        img = car._camera.frames()[0]
        lines = car._lane_detector.process(img)
        img_with_lines = car._lane_detector.draw_lines_on_img(img, lines)
        # cv2.imshow('img with lines', img_with_lines)
        # cv2.waitKey(0)
        state = car.state()
        print(len(state))
