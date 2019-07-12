import traceback
import aiohttp_cors
import threading
import asyncio
import aiohttp
from aiohttp import web, MultipartWriter
import socketio
from radar_socket import RadarSocket
from camera_socket import CameraSocket
from collections import deque
import os
import sys
import logging
logger = logging.getLogger(__name__)

''' VARIABLES '''
camera_socket = CameraSocket(addr='tcp://127.0.0.1:8089')
radar_socket = RadarSocket(addr='tcp://127.0.0.1:8090')

''' AIOHTTP '''


async def index(request):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, './templates/index.html')
    return web.FileResponse(filename)


async def camera_feed(request):

    response = web.StreamResponse(status=200, headers={
                                  'Content-Type': 'multipart/x-mixed-replace;boundary=--frame'})

    await response.prepare(request)

    async with aiohttp.ClientSession() as client:
        while True:
            frame = camera_socket.get_frame()

            if frame:
                with MultipartWriter('image/jpeg', boundary='frame') as mpwriter:
                    mpwriter.append(frame, {'Content-Type': 'image/jpeg'})
                    await mpwriter.write(response, close_boundary=False)
            # release event loop
            await asyncio.sleep(0.1)

    return response


app = web.Application()

app.add_routes([web.get('/', index),
                web.get('/camera_feed.mjpg', camera_feed)])
# Cors all routes
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})
for route in list(app.router.routes()):
    cors.add(route)

''' SOCKET IO '''
sio = socketio.AsyncServer(async_mode='aiohttp')
sio.attach(app)


async def emit_radar():
    logger.info("Starting radar emitting task...")
    while True:
        value = radar_socket.get_value()
        if not value:
            continue
        await sio.emit("new value", value, namespace="/radar")
        await asyncio.sleep(0.01)


def start():
    loop = asyncio.get_event_loop()
    loop.create_task(emit_radar())
    logger.info("Starting server...")
    web.run_app(app)
