import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

import server

if __name__ == '__main__':
    server.start()
