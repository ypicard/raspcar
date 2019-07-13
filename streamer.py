import threading
import socket
from collections import deque
import logging
logger = logging.getLogger(__name__)
import zmq
import cv2

class CameraStreamer(threading.Thread):
    __slots__ = '_socket', '_camera', '_lock'

    def __init__(self, camera, addr):
        context = zmq.Context()
        self._camera = camera
        self._socket = context.socket(zmq.REP)
        self._socket.bind(addr)
        self._lock = threading.Lock()
        self.start()

    def run(self):
        while True:
            # send img through socket asap
            with self._lock:
                if self._camera._frames.empty():
                    continue
                img = self._camera._frames[0]
            # encode img to byte buffer
            success, img = cv2.imencode('.png', img)
            logger.debug('sending frame')
            self._socket.send(img)
