from radar_streamer import RadarStreamer
import config
import logging
from time import sleep, time
import RPi.GPIO as GPIO
import threading
logger = logging.getLogger(__name__)

class Radar(threading.Thread):
    ''' HC-SR04 module python implementation '''

    __slots__ = 'name', '_streamer', '_trigger_gpio', '_echo_gpio', '_distance', '_lock'

    def __init__(self, name, trigger_gpio, echo_gpio):
        super(Radar, self).__init__()
        self.name = name
        self._distance = None
        self._lock = threading.Lock()
        self._streamer = RadarStreamer(self, addr=config.RADARS['address'])
        self._trigger_gpio = trigger_gpio
        self._echo_gpio = echo_gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._trigger_gpio, GPIO.OUT)
        GPIO.setup(self._echo_gpio, GPIO.IN)
        self.start()

    def run(self):
        while True:
            # set Trigger to HIGH
            GPIO.output(self._trigger_gpio, True)
            # set Trigger after 0.01ms to LOW
            sleep(0.00001)
            GPIO.output(self._trigger_gpio, False)

            start_time = time()
            stop_time = time()

            # save start_time
            while GPIO.input(self._echo_gpio) == 0:
                start_time = time()

            # save stop_time
            while GPIO.input(self._echo_gpio) == 1:
                stop_time = time()

            time_elapsed = stop_time - start_time
            # multiply by sonic speed 340m/s and divide by 2, because back and forth
            with self._lock:
                distance = (time_elapsed * 340) / 2
                distance = round(distance, 2) # round 2 decimals
                self._distance = distance

    def get_distance(self):
        with self._lock:
            return self._distance

if __name__ == '__main__':
    trigger = 18
    echo = 24
    radar = Radar(trigger, echo)

    try:
        while True:
            dist = radar.distance()
            print("Measured Distance = %.1f m" % dist)
            sleep(1)

    finally:
        GPIO.cleanup()
