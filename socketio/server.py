import logging
from collections import deque
from camera_socket import CameraSocket
from radar_socket import RadarSocket
import socketio
from aiohttp import web
import asyncio
from time import sleep
import threading

async def index(request):
    return web.FileResponse('./templates/index.html')

async def camera_feed(request):
    def get_img():
        while True:
            frame = camera_socket.get_frame()
            if not frame:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

    return web.Response(get_img(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

app = web.Application()
app.add_routes([web.get('/', index),
                web.get('/camera_feed.mjpg', index)])
sio = socketio.AsyncServer(async_mode='aiohttp')
sio.attach(app)


async def emit_radar():
    while True:
        value = radar_socket.get_value()
        if not value:
            continue
        await sio.emit("new value", value, namespace="/radar")

@sio.event( namespace="/radar")
def connect(sid, environ):
    print('radar socket connected ', sid)
    asyncio.create_task(emit_radar())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # camera_socket = CameraSocket(host='localhost', port=8089, frame_size=2730)
    radar_socket = RadarSocket(host='localhost', port=8090)
    logging.info("Starting Flask server")
    web.run_app(app)