import logging
import threading
from collections import deque
import zmq
logger = logging.getLogger(__name__)

class CameraSocket(threading.Thread):

    def __init__(self, addr):
        super(CameraSocket, self).__init__(daemon=True)
        context = zmq.Context()
        self._socket = context.socket(zmq.REP)
        self._socket.bind(addr)
        self._frames = deque(maxlen=10)
        self.start()

    def run(self):
        logger.debug('CameraSocket waiting for connection')
        while True:
            buffer = self._socket.recv()
            self._socket.send_string('ok')
            logger.debug("frame received")
            bytes_img = buffer
            # # use numpy to construct an array from the bytes
            # png_img = np.frombuffer(bytes_img, dtype='uint8')
            # # decode the array into an image
            # numpy_img = cv2.imdecode(png_img, cv2.IMREAD_COLOR)
            # # base 64 encode string
            # base64_img_str = base64.b64encode(png_img).decode()
            # save img in queue
            self._frames.append(bytes_img)


    def get_frame(self):
        ''' Get frame in bytes if available '''
        if not self._frames:
            return
        # frame in bytes
        return self._frames.popleft()
