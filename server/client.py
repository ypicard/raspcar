from time import sleep
import sys
import numpy as np
import cv2
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:8089")


def gen_img():
    img = np.uint8(255 * np.random.rand(50, 50))
    success, img = cv2.imencode('.png', img)
    return img


while True:
    img = gen_img()
    print(f'Bytes to be sent: {sys.getsizeof(img)}')

    socket.send(img)
    socket.recv()
    sleep(1/10)  # fps
