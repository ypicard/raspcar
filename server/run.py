# kill -9 $(ps aux | grep  python | awk '{print $2}')
import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
import server

if __name__ == '__main__':
    server.start()
