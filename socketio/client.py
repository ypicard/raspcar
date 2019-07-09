import socket
import numpy as np
import sys
import cv2

# Use one socket for images, one socket for other data

def encode_img(img):
    """Encodes an image as a png and encodes to base 64 for display."""
    success, encoded_img = cv2.imencode('.png', img)
    return encoded_img

img = np.uint8(255 * np.random.rand(50, 50))
print(img)
img_encoded = encode_img(img).tostring()
print(f'Bytes to be sent: {sys.getsizeof(img_encoded)}')
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 8089))
clientsocket.send(img_encoded)
