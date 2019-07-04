import cv2
from matplotlib import pyplot as plt
import numpy as np


def convert_hls(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2HLS)


def convert_gray_scale(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def select_white_yellow(image):
    converted = convert_hls(image)
    # white color mask
    lower = np.uint8([0, 200,   0])
    upper = np.uint8([255, 255, 255])
    white_mask = cv2.inRange(converted, lower, upper)
    # yellow color mask
    lower = np.uint8([90,   80, 100])
    upper = np.uint8([110, 255, 255])
    yellow_mask = cv2.inRange(converted, lower, upper)
    # combine the mask
    mask = cv2.bitwise_or(white_mask, yellow_mask)
    return cv2.bitwise_and(image, image, mask=mask)


def gaussian_smoothing(img, kernel_size=15):
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def canny_edges(img, low=50, high=150):
    return cv2.Canny(img, low, high)


def filter_region(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    return cv2.bitwise_and(img, mask)


def select_region(img):
    rows, cols = img.shape
    bottom_left = [cols*0.1, rows*0.95]
    top_left = [cols*0.4, rows*0.6]
    bottom_right = [cols*0.9, rows*0.95]
    top_right = [cols*0.6, rows*0.6]
    vertices = np.array([[bottom_left, top_left, top_right,
                          bottom_right]], dtype=np.int32)
    return filter_region(img, vertices)

def hough_lines(img):
        return cv2.HoughLinesP(img, rho=1, theta=np.pi/180, threshold=20, minLineLength=20, maxLineGap=300)

if __name__ == "__main__":
    img = cv2.imread('./lane_detection/images/YellowUnderShade2.jpg')  # rgb
    img = select_white_yellow(img)
    img = convert_gray_scale(img)
    img = gaussian_smoothing(img)
    img = canny_edges(img)
    img = select_region(img)
    lines = hough_lines(img)
    for line in lines:
        x1,y1,x2,y2 = line[0]
        cv2.line(img, (x1,y1), (x2,y2), (0,255,0), 1)
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
