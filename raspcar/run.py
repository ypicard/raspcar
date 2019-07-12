import logging
logger = logging.getLogger(__name__)
from car import Car
import yaml
import traceback

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Starting main script")
    config = yaml.safe_load(open('config.yaml'))
    car = Car()
    try:
        while True:
            logging.debug('Loop start')
            car.update()
            
    except Exception:
        print(traceback.print_exc())
