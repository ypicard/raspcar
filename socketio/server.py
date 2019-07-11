import logging
from collections import deque
from camera_socket import CameraSocket
from radar_socket import RadarSocket
import socketio
from aiohttp import web, MultipartWriter
import asyncio
from time import sleep
import threading
import aiohttp_cors
import traceback

async def index(request):
    return web.FileResponse('./templates/index.html')


    

async def camera_feed(request):
    
    response = web.StreamResponse(status=200,headers={'Content-Type': 'multipart/x-mixed-replace;boundary=--frame'})

    await response.prepare(request)
    # asyncio.create_task(send_img(response))
    while True:
        frame = camera_socket.get_frame()
        try:
            if frame:
                with MultipartWriter('image/jpeg', boundary='frame') as mpwriter:
                    print("writing")
                    mpwriter.append(frame, {'Content-Type': 'image/jpeg'})
                    await mpwriter.write(response, close_boundary=False)
            # release event loop
            await asyncio.sleep(0.01)
            
        except Exception as e:
            # disconnect
            print(repr(e))
            # raise
            traceback.print_tb(e.__traceback__)
            raise

    return response


app = web.Application()
cors = aiohttp_cors.setup(app)

app.add_routes([web.get('/', index),
    web.get('/camera_feed.mjpg', camera_feed)])

sio = socketio.AsyncServer(async_mode='aiohttp')
sio.attach(app)


async def emit_radar():
    while True:
        value = radar_socket.get_value()
        if not value:
            continue
        await sio.emit("new value", value, namespace="/radar")

# @sio.event( namespace="/radar")
# def connect(sid, environ):
#     print('radar socket connected ', sid)
#     asyncio.create_task(emit_radar())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    camera_socket = CameraSocket(host='localhost', port=8089, frame_size=2730)
    # radar_socket = RadarSocket(host='localhost', port=8090)
    logging.info("Starting Flask server")
    web.run_app(app)
