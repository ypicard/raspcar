import socket
from flask import Flask, Response
import threading
import numpy as np
import cv2
app = Flask(__name__)
from collections import deque
import base64 

data_queue = deque(maxlen=10)
FRAME_SIZE_BYTES = 2730

def launch_socket_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8089))
    server_socket.listen(5) # become a server socket, maximum 5 connections
    print(f"Socker server listening on port {8089}")
    connection, address = server_socket.accept()
    
    while True:
        buffer = connection.recv(FRAME_SIZE_BYTES)

        if len(buffer) > 0:
            bytes_img = buffer
            # use numpy to construct an array from the bytes
            png_img = np.frombuffer(bytes_img, dtype='uint8')
            # decode the array into an image
            numpy_img = cv2.imdecode(png_img, cv2.IMREAD_COLOR)
            # base 64 encode string
            base64_img_str = base64.b64encode(png_img).decode()
            # save img in queue
            data_queue.append(bytes_img)


PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

@app.route("/")
def hello():
    return PAGE


def gen():
    while True:
        if not data_queue:
            continue
        # frame in bytes
        frame = data_queue.popleft()

        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')
        

@app.route("/stream.mjpg")
def stream():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

print("Start thread")
t = threading.Thread(target=launch_socket_server)
t.start()

print("Start flask")
app.run(host='localhost', port=8080)