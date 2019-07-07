import io
import time
import threading
import picamera


class ProcessOutput(object):
    def __init__(self, owner):
        self.done = False
        self._owner = owner

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self._owner.stream.write(buf)


class VideoFeed():
    def __init__(self, owner):
        self._owner = owner
        self.stream = io.BytesIO()

        with picamera.PiCamera(resolution='VGA') as camera:
            camera.start_preview()
            time.sleep(2)
            output = ProcessOutput(self)
            camera.start_recording(output, format='mjpeg')
            while not output.done:
                camera.wait_recording(1)
            camera.stop_recording()

    def get_img(self):
        try:
            self.stream.seek(0)
            print(self.stream)
            # Read the image and do some processing on it
            # Image.open(self.stream)
            # ...
            # ...
            # Set done to True if you want the script to terminate
            # at some point
            # self.owner.done=True
        finally:
            # Reset the stream and event
            self.stream.seek(0)
            self.stream.truncate()


class LaneDetector():
    def __init__(self, owner):
        self._owner = owner


class RadarMaster():
    def __init__(self, owner):
        self._owner = owner


class Car():
    def __init__(self):
        self.video_feed = VideoFeed(self)
        self.lane_detector = LaneDetector(self)
        self.radar_master = RadarMaster(self)

    def update(self):
        self.video_feed.get_img()
        # lanes = LaneDetector.detect(img)
        # radar_values = RadarCenter().get_values()
        # state = [lanes, radar_values, ...]
        # action = agent.act(state)
        # car.act(action)


if __name__ == "__main__":

    car = Car()
    while True:
        car.update()
