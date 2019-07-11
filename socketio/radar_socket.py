import logging
import socket
import threading
from collections import deque
from time import sleep

class RadarSocket(threading.Thread):

    def __init__(self, host, port):
        super(RadarSocket, self).__init__(daemon=True)
        self._host = host
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._values = deque(maxlen=10)
        self._socket.bind((self._host, self._port))
        self._socket.listen(5) # become a server socket, maximum 5 connections
        logging.info("RadarSocket listening")
        
        self.start()

    def run(self):
        while True:
            print("append values")
            self._values.append(3)
            sleep(1)
        # logging.debug('RadarSocket waiting for connection...')
        # connection, address = self._socket.accept()
        # while True:
        #     buffer = connection.recv(self._frame_size)

        #     if len(buffer) > 0:
        #         logging.debug("value received")
        #         bytes_img = buffer
        #         # # use numpy to construct an array from the bytes
        #         # png_img = np.frombuffer(bytes_img, dtype='uint8')
        #         # # decode the array into an image
        #         # numpy_img = cv2.imdecode(png_img, cv2.IMREAD_COLOR)
        #         # # base 64 encode string
        #         # base64_img_str = base64.b64encode(png_img).decode()
        #         # save img in queue
        #         self._values.append(bytes_img)


    def get_value(self):
        ''' Get value if available '''
        if not self._values:
            return

        return self._values.popleft()
