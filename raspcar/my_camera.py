import logging
from picamera import PiCamera
from picamera.array import PiRGBArray
import threading
from collections import deque
from time import sleep

class MyCamera(threading.Thread):
    ''' Raspberry camera module python implementation '''

    __slots__ = '_camera', '_stream', '_frames'

    def __init__(self, resolution=(640, 480), framerate=30, nb_frames=5):
        super(MyCamera, self).__init__()
        logging.debug("MyCamera.__init__")
        self._camera = PiCamera()
        self._camera.resolution = resolution
        self._camera.framerate = framerate 
        self._stream = PiRGBArray(self._camera)
        self._frames = deque(maxlen=nb_frames)
        self.start()

    def run(self):
        for frame in self._camera.capture_continuous(self._stream, format='bgr', use_video_port=True):
            # Append each new frame to deque
            img = frame.array # numpy array img
            self._frames.append(img)
            # Truncate and reset read position for next frames
            self._stream.truncate()
            self._stream.seek(0)

    def frames(self):
        return self._frames


if __name__ == '__main__':
    camera = MyCamera()
    while True:
        frames = camera.frames()
        sleep(0.1)
        print(len(frames))
