import logging
logger = logging.getLogger(__name__)
from car import Car
import traceback

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Starting main script")
    car = Car()
    try:
        while True:
            logging.debug('Loop start')
            car.update()
            
    except Exception:
        print(traceback.print_exc())
