import cv2
from matplotlib import pyplot as plt
import numpy as np


def convert_hls(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2HLS)


def convert_gray_scale(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def select_white_yellow(image):
    converted = convert_hls(image)
    cv2.imshow('image', converted)
    cv2.waitKey(0)
    # white color mask
    lower = np.uint8([0, 200,   0])
    upper = np.uint8([255, 255, 255])
    white_mask = cv2.inRange(converted, lower, upper)
    # yellow color mask
    lower = np.uint8([10,   0, 100])
    upper = np.uint8([40, 255, 255])
    yellow_mask = cv2.inRange(converted, lower, upper)
    # combine the mask
    mask = cv2.bitwise_or(white_mask, yellow_mask)
    return cv2.bitwise_and(image, image, mask=mask)


if __name__ == "__main__":
    img = cv2.imread('./lane_detection/images/YellowUnderShade2.jpg')  # rgb

    img = select_white_yellow(img)
    # img = convert_gray_scale(img)
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
