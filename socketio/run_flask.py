import socket
from flask import Flask
import threading
import numpy as np
import cv2
app = Flask(__name__)

data = []
FRAME_SIZE_BYTES = 2651

def launch_socket_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8089))
    server_socket.listen(5) # become a server socket, maximum 5 connections
    print(f"Socker server listening on port {8089}")
    connection, address = server_socket.accept()
    
    while True:
        buffer = connection.recv(FRAME_SIZE_BYTES)
        print(len(buffer))
        img = np.frombuffer(buffer, dtype='uint8')
        img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)
# yann
        # cv2.imshow('test', img)
        # cv2.waitKey(1)

        # if len(buffer) > 0:
        #     print('buffer' + str(buffer))
        #     data.append(buffer.decode())


@app.route("/")
def hello():
    return "Hello World! " + str(len(data))


print("Start thread")
t = threading.Thread(target=launch_socket_server)
t.start()

print("Start flask")
app.run(host='localhost', port=8080)
