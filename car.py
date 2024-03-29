import config
from camera_streamer import CameraStreamer
from agent import Agent
from camera import Camera
from radar import Radar
import io
from time import sleep
import cv2
import logging
logger = logging.getLogger(__name__)


class Car():

    __slots__ = '_camera', '_radars', '_agent', '_camera_streamer', 'state'

    def __init__(self):
        self._camera = Camera()
        self._radars = [Radar('test', 18, 24)]
        self._agent = Agent()
        # self._camera_streamer = CameraStreamer(
        #    self._camera, addr=config.CAMERA['address'])

    def update(self):
        state = self.get_state()
        action = self._agent.predict(state)
        # logger.debug(f'action={action}')
        self._act(action)
        self.state = state

    def _act(self, action):
        pass

    def get_state(self):
        state = []
        # radar states
        for radar in self._radars:
            state.append(radar.get_distance())
        # video state
        state += self._camera.lanes()

        return state


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    car = Car()
    sleep(2)
    while True:
        img = car._camera.frames()[0]
        lines = car._lane_detector.process(img)
        img_with_lines = car._lane_detector.draw_lines_on_img(img, lines)
        # cv2.imshow('img with lines', img_with_lines)
        # cv2.waitKey(0)
        state = car.get_state()
