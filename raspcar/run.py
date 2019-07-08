from car import Car
import logging
import traceback

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting main script")
    car = Car()
    try:
        while True:
            logging.debug('Loop start')
            car.update()
    except Exception:
        print(traceback.print_exc())
