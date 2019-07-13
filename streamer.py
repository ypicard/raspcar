import threading
import socket
from collections import deque
import logging
logger = logging.getLogger(__name__)
import zmq
import cv2

class CameraStreamer(threading.Thread):
    __slots__ = '_socket', '_camera'

    def __init__(self, camera, addr):
        super(CameraStreamer, self).__init__(daemon=True)
        logger.info(f"connecting to {addr}")
        context = zmq.Context()
        self._camera = camera
        self._socket = context.socket(zmq.REQ)
        self._socket.connect(addr)
        self.start()

    def run(self):
        while True:
            # send img through socket asap
            frame = self._camera.last_frame()
            if frame is None:
                continue
            # encode img to byte buffer
            print(frame)
            success, img = cv2.imencode('.png', frame)
            logger.debug('sending frame')
            self._socket.send(img)
            self._socket.recv()
