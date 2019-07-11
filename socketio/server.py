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
                    await mpwriter.write(response)
            await asyncio.sleep(0.01)
            
        except Exception as e:
            # So you can observe on disconnects and such.
            print(repr(e))
            # raise
            traceback.print_tb(e.__traceback__)
            raise

    return response
    # try:
    #     while True:
    #         frame = camera_socket.get_frame()
    #         if not frame:
    #             continue

    #         data = b'--frame\r\nContent-Type: image/png\r\n\r\n' + frame + b'\r\n'
    #         await response.write(data)
    # finally:
    #     await resp.write_eof()
    # return response

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