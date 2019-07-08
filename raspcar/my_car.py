from time import sleep
import cv2
import logging
import io
import my_radar
import my_camera

class Car():

    __slots__ = '_camera', '_radars'
    
    def __init__(self):
        logging.debug("Car.__init__")
        self._camera = my_camera.MyCamera()
        self._radars = [my_radar.MyRadar(18, 24)]

    def state(self):
        state = []
        for radar in self._radars:
            state.append(radar.distance())
        state += self._camera.frames()

        return state

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting script...")
    car = Car()
    sleep(2)
    while True:
       # img = car._camera.frames()[0]
       # cv2.imshow('live feed', img)
       # cv2.waitKey(1)
       state = car.state()
       print(len(state))

