from time import sleep
import threading
import socket
from collections import deque
import logging
logger = logging.getLogger(__name__)
import zmq

class RadarStreamer(threading.Thread):
    __slots__ = '_socket', '_radar', '_lock'

    def __init__(self, radar, addr):
        super(RadarStreamer, self).__init__(daemon=True)
        self._lock = threading.Lock()
        logger.info(f"connecting to {addr}")
        context = zmq.Context()
        self._radar = radar
        self._socket = context.socket(zmq.PUB)
        self._socket.connect(addr)
        self.start()

    def run(self):
        while True:
            value = self._radar.get_distance()
            if value is None:
                continue
            logger.debug(f'sending {value}')
            self._socket.send_string(f'{self._radar.name} {value}')
            sleep(0.1)
