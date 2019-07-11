import logging
from collections import deque
from flask import Flask, Response, render_template
from camera_socket import CameraSocket
from radar_socket import RadarSocket
import socketio
from flask_cors import CORS
from time import sleep
import threading

sio = socketio.Server(async_mode='threading')
app = Flask(__name__)
CORS(app)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

@app.route("/")
def home():
    return render_template('index.html')


@app.route("/camera_feed.mjpg")
def camera_feed():
    def get_img():
        while True:
            frame = camera_socket.get_frame()
            if not frame:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

    return Response(get_img(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



@sio.event( namespace="/radar")
def connect(sid, environ):
    print('radar socket connected ', sid)
    sio.emit("new value", "ok", namespace="/radar")



# @socketio.on('connect', namespace="/radar")
# def radar_socket_connected():
#     print("SHOULD GO IN")
#     def get_value():
#         print("MDR")
#         while True:
#             value = radar_socket.get_value()
#             if not value:
#                 continue
#             print('should emit')
#             emit('new value', value)

#     print("RADAR CONNECTED")
#     thread = threading.Thread(target = get_value)
#     thread.start()
#     emit('lol')
    




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    camera_socket = CameraSocket(host='localhost', port=8089, frame_size=2730)
    radar_socket = RadarSocket(host='localhost', port=8090)
    logging.info("Starting Flask server")
    app.run(threaded=True)