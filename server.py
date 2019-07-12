import socket
import numpy as np
import cv2

PORT = 8089
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', PORT))
serversocket.listen(5) # become a server socket, maximum 5 connections
print(f"Server listening on port {PORT}")

while True:
    connection, address = serversocket.accept()
    buf = connection.recv(2651) # same nb of bytes

    if len(buf) > 0:
        img = np.fromstring(buf, dtype='uint8')
        img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)

        cv2.imshow('live stream', img)
        cv2.waitKey(1)

        
        