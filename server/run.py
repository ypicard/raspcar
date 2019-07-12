# kill -9 $(ps aux | grep  python | awk '{print $2}')
import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

import server

if __name__ == '__main__':
    server.start()
