from car import Car
from streamer import Streamer
import logging
import traceback

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting main script")
    car = Car()
    streamer = Streamer('localhost', 8089)
    try:
        while True:
            logging.debug('Loop start')
            car.update()
            state = car.state
            streamer.queue_frame(state[1])
            
    except Exception:
        print(traceback.print_exc())
