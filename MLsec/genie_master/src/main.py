import os
print(os.getcwd())
print(os.path.abspath(__file__))
#os.chdir(p)
print(os.listdir())
print(os.listdir("C:\\Users\\puria\\source\\repos\\puria-radmard\\CambridgeCarbonMap\MLsec\genie_master\src"))
os.chdir("C:\\Users\\puria\\source\\repos\\puria-radmard\\CambridgeCarbonMap\\MLsec\\genie_master\\src")
print(os.listdir())

import argparse
import numpy as np
import cv2
import keras
import matplotlib.pyplot as plt

import cv2
import numpy as np


def img_resize(img, img_size):
    """Function creates empty np.arrays of the specified dimensions to act as blank image
    Args:
        param1 (np.array): image to resize
        param2 (int, int): (x, y) dimensions of output image
    Returns:
        (np.array): image of requested dimensions
    """
    return cv2.resize(img, img_size, interpolation=cv2.INTER_AREA)


def read_img(img_path):
    return cv2.imread(img_path)


def create_emptyimg(img_size):
    """Function creates empty np.arrays of the specified dimensions to act as blank image
    Args:
        param1 (int, int): (x, y) dimensions of blank image
    Returns:
        np.array[int][int] of zeros
    """
    return np.zeros([img_size[1], img_size[0]], np.uint8)


def extract_roi(image, img_size=(250, 30), verbose=False):
    '''Function extracting the ROI and preprocessing it.

    If no ROI is detected, empty image of the specified size is returned. Note that the annotated input image is never resized.

    Args:
        param1 (str): The path of input image.
        [param2 (2-tuple): The size of output ROI.]
        [param3 (bool, [False]), specify whether the input image is returned with annotations.]

    Returns:
        bool = False (default): roi_gray, roi_thresh
        bool = True: img, roi_gray, roi_thresh
    '''

    (ih, iw, _) = image.shape
    img = image.copy()

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    gray_thresh = np.uint8(np.where(gray > 140, 255, 0))
    kernel = np.ones((5, 5), np.uint8)
    gray_thresh = cv2.erode(gray_thresh, kernel, iterations=2)
    gray_thresh = cv2.dilate(gray_thresh, kernel, iterations=2)
    # # reduce noise
    # blur = cv2.GaussianBlur(gray, (7, 7), 0)
    # blur = gray
    # edge detection using Canny
    canny = cv2.Canny(gray_thresh, 50, 150)

    contours, hierarch = cv2.findContours(canny.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    detected = False
    contour = []

    # loop over the contours
    for cnt in contours:
        ## Get the stright bounding rect
        x, y, w, h = cv2.boundingRect(cnt)
        (cx, cy) = (int(x + w / 2), int(y + h / 2))

        if (w > 100 and h > 25) and (w < 300 and h < 100) and (
                iw / 2 - 0.05 * iw < cx < iw / 2 + 0.05 * iw and ih / 2 - 0.05 * ih < cy < ih / 2 + 0.05 * ih):
            contour.append(cnt)
            detected = True

            break

    if detected is True:

        img_roi = image[y:y + h, x:x + w]
        roi_gray = cv2.bitwise_not(cv2.cvtColor(img_roi, cv2.COLOR_RGB2GRAY))
        roi_blur = cv2.medianBlur(roi_gray, 3)

        roi_thresh = cv2.adaptiveThreshold(roi_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
        roi_thresh = cv2.medianBlur(roi_thresh, 3)

        kernel = np.ones((2, 2), np.uint8)
        roi_thresh = cv2.dilate(roi_thresh, kernel, iterations=2)
        roi_thresh = cv2.erode(roi_thresh, kernel, iterations=1)
        # roi_thresh = cv2.medianBlur(roi_thresh, 3)

        if verbose is False:
            return img_resize(roi_gray, img_size), img_resize(roi_thresh, img_size)
        else:
            # Reference
            cv2.drawMarker(img, (int(iw / 2), int(ih / 2)), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20,
                           thickness=3, line_type=cv2.LINE_AA)
            cv2.rectangle(img, (int(iw / 2 - 0.05 * iw), int(ih / 2 - 0.05 * ih)),
                          (int(iw / 2 + 0.05 * iw), int(ih / 2 + 0.05 * ih)), (0, 255, 0), 2)
            # draw contour
            cv2.drawContours(img, contour, -1, (255, 0, 0), 2)

            ## Draw rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2, 16)
            cv2.drawMarker(img, (cx, cy), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=3,
                           line_type=cv2.LINE_AA)

            return img, img_resize(roi_gray, img_size), img_resize(roi_thresh, img_size)


    else:

        empty_img = create_emptyimg(img_size)

        if verbose is False:
            return img_resize(empty_img, img_size), img_resize(empty_img, img_size)
        else:
            cv2.putText(img, 'No meter reading detected', (int(iw / 2 - 200), int(ih / 2 - 100)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return img, img_resize(empty_img, img_size), img_resize(empty_img, img_size)


def remove_border(image):
    image[:3, :] = 255
    image[-3:, :] = 255
    image[:, :3] = 255
    image[:, -3:] = 255
    return image


def Euclidean(vec1, vec2):
    """
    Euclidean_Distance
    :param vec1:
    :param vec2:
    :return:
    """
    npvec1, npvec2 = np.array(vec1), np.array(vec2)
    return np.sqrt(((npvec1 - npvec2) ** 2).sum())


def extract_digit(image, raw_image=None, inc_last=False):
    mser = cv2.MSER_create(_min_area=50, _max_area=100)
    regions, boxes = mser.detectRegions(image)
    fewer_boxes = []
    distinct_boxes = []
    digits = []

    # removing duplicates
    for box in boxes.tolist():
        if box not in fewer_boxes:
            fewer_boxes.append(box)

    # print(len(fewer_boxes))

    # removing similar
    for j in fewer_boxes:
        if distinct_boxes:
            if Euclidean(j, distinct_boxes[-1]) > 15:
                distinct_boxes.append(j)
        else:
            distinct_boxes.append(j)

    # print(len(distinct_boxes))

    # extracting digits and store to a list
    for box in distinct_boxes[:8]:
        x, y, w, h = box
        if raw_image is None:
            digit = image[y - 2:y + h + 2, x - 2:x + w + 2]
        else:
            digit = raw_image[y - 2:y + h + 2, x - 2:x + w + 2]
        digit = img_resize(digit, (28 // digit.shape[0] * digit.shape[1], 28))
        if digit.shape[1] < 32:
            dleft, dright = (32 - digit.shape[1]) // 2, (32 - digit.shape[1]) - ((32 - digit.shape[1]) // 2)
            digit = cv2.copyMakeBorder(digit, 2, 2, dleft, dright, cv2.BORDER_CONSTANT, value=255)
        else:
            digit = img_resize(cv2.copyMakeBorder(digit, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=255), (32, 32))
        digits.append(digit)

    return digits[:7] if inc_last else digits


if __name__ == '__main__':
    img, roi_gray, roi_thresh = extract_roi(read_img('test.png'), verbose=True)

    # print(roi_gray.shape)

    cv2.imshow('Image', img)
    cv2.imshow('ROI', roi_gray)
    cv2.imshow('Threshed', remove_border(roi_thresh))

    digits = extract_digit(remove_border(roi_thresh))

    for i in range(len(digits)):
        # digits[i] = cv2.adaptiveThreshold(digits[i], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
        # kernel = np.ones((5, 5))
        # digits[i] = cv2.erode(digits[i], kernel, iterations=1)
        # digits[i] = cv2.blur(digits[i], (5, 5))
        # text = pytesseract.image_to_string(digits[i])
        # print(text)
        cv2.imwrite('./' + str(i) + '.png', digits[i])

    cv2.waitKey(0)

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal


# signal processing techniques to remove outlier and smooth the plot

def smooth(vec):
    vec = signal.medfilt(vec, kernel_size=51)
    win = np.ones(15)
    vec = signal.fftconvolve(vec, win, mode='valid') / sum(win)

    return vec


if __name__ == '__main__':
    vec = np.loadtxt('../data/data.csv', delimiter=',')
    plt.plot(np.arange(1, len(vec) + 1, 1), vec)
    plt.plot(np.arange(1, len(smooth(vec)) + 1, 1), smooth(vec))
    # plt.ylim([7.5e6, 7.6e6])
    plt.show()


#from Preprocessor import *
#from Postprocessor import *

parser = argparse.ArgumentParser(prog='main', usage='%(prog)s [options] path',
                                 description='Recognise gas meter reading')
parser.add_argument('--clear', action='store_true', help='clear the output directory', required = False)
parser.add_argument('-s', '--save', action='store_true', help='save the recognised data as csv', required = False)
parser.add_argument('-r', '--raw', action='store_true', help='show raw data', required = False)
parser.add_argument('Path', metavar='path', type=str, nargs='+', help='the path to raw images')

args = parser.parse_args(["Path"])
input_path = args.Path

model = keras.models.load_model('../model/detector_model_1.hdf5')
#print(model.summary())

result = []


# Print iterations progress from https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
	Call in a loop to create terminal progress bar
	@params:
		iteration   - Required  : current iteration (Int)
		total       - Required  : total iterations (Int)
		prefix      - Optional  : prefix string (Str)
		suffix      - Optional  : suffix string (Str)
		decimals    - Optional  : positive number of decimals in percent complete (Int)
		length      - Optional  : character length of bar (Int)
		fill        - Optional  : bar fill character (Str)
		printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
	"""
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


# if False:#args.clear:
#     print("Removing all the images")
#     os.system('(cd {} && rm ./*.png)'.format('../data/result/'))

# else:

def dummyPredict(image_addr):
        for path in input_path:
            roi_gray, roi_thresh = extract_roi(read_img(image_addr))  #path))
            try:
                digits = extract_digit(remove_border(roi_thresh))
                texts = []

                for i in range(len(digits)):
                    digit = digits[i]
                    # kernel = np.ones((2, 2), np.uint8)
                    # digit = cv2.dilate(digit, kernel, iterations=1)
                    digit = np.dstack([digit, digit, digit])
                    digit = digit.reshape((1, 32, 32, 3))
                    prediction = model.predict(digit)
                    digit_predict = np.argmax(prediction)
                    if i == 0:
                        digit_predict = 0
                    if digit_predict == 10:
                        digit_predict = 0
                    texts.append(str(digit_predict))
            except:
                texts = ['0']

            outstr = ''.join(texts)
            print(outstr)
            return(int(outstr)/10)