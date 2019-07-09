import logging
from picamera import PiCamera
from picamera.array import PiRGBArray
import threading
from collections import deque
from time import sleep
from lane_detector import LaneDetector


class Camera(threading.Thread):
    ''' Raspberry camera module python implementation '''

    __slots__ = '_camera', '_stream', '_frames', '_frames_processed', '_lane_detector', '_lock'

    def __init__(self, resolution=(640, 480), framerate=30, nb_frames=5):
        super(MyCamera, self).__init__()
        logging.debug("MyCamera.__init__")
        self._lock = threading.Lock()
        self._camera = PiCamera()
        self._camera.resolution = resolution
        self._camera.framerate = framerate
        self._stream = PiRGBArray(self._camera)
        self._lane_detector = LaneDetector()
        self._frames = deque(maxlen=nb_frames)
        self._frames_processed = deque(maxlen=nb_frames)
        self.start()

    def run(self):
        for frame in self._camera.capture_continuous(self._stream, format='bgr', use_video_port=True):
            # New frame in numpy format
            img = frame.array
            # Detect lanes in each frames
            img_processed = self._lane_detector.process(img)
            # Truncate and reset read position for next frames
            self._stream.truncate()
            self._stream.seek(0)

            # Store frames with thread lock
            with self._lock:
                self._frames.append(img)
                self._frames_processed.append(img_processed)

    def lanes(self):
        with self._lock:
            return list(self._frames_processed)


if __name__ == '__main__':
    camera = MyCamera()
    while True:
        frames = camera.frames()
        sleep(0.1)
        print(len(frames))
