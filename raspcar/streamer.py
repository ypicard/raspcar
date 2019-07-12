import threading
import socket
from collections import deque
import logging
logger = logging.getLogger(__name__)
import zmq

class CameraStreamer(threading.Thread):
    __slots__ = '_socket', '_camera', '_lock'

    def __init__(self, camera, addr):
        context = zmq.Context()
        self._socket = context.socket(zmq.REP)
        self._socket.bind(addr)
        self._lock = threading.Lock()
        self.start()

    def run(self):
        while True:
            # send img through socket asap
            with self._lock:
                if self._camera._frames.empty():
                    return
                img = self._camera._frames[0]
            # encode img to byte buffer
            img = encode_img(img).tostring()
            logger.debug('sending frame')
            self._socket.send(img)