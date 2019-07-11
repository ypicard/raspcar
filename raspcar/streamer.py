import threading
import socket
from collections import deque
import logging
logger = logging.getLogger(__name__)


class Streamer(threading.Thread):
    __slots__ = '_host', '_port', '_socket', '_frames', '_lock'

    def __init__(self, host, port):
        logger.debug('Streamer.__init__')
        self.frames = deque(maxlen=5)
        self._lock = threading.Lock()
        self._host = host
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start()

    def run(self):
        self._socket.connect((self._host, self._port))
        while True:
            # send img through socket asap
            with self._lock:
                logger.debug(f'{len(_frames)} waiting for socket')
                if q.empty():
                    return
                img = self._frames.popleft()

            # encode img to byte buffer
            img = encode_img(img).tostring()
            logger.debug(f'Bytes to be sent: {sys.getsizeof(img)}')
            
            self._socket.send(img)

    def queue_frame(self, img):
        with lock:
            self._frames.append(img)