import socket
from time import sleep
import sys
import numpy as np
import cv2


def gen_img():
    img = np.uint8(255 * np.random.rand(50, 50))
    success, png_img = cv2.imencode('.png', img)
    buf_img = png_img.tostring()
    return png_img


clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 8089))
while True:
    img = gen_img()
    print(len(img))
    print(f'Bytes to be sent: {sys.getsizeof(img)}')

    clientsocket.send(img)
    sleep(5)