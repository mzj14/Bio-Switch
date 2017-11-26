from urllib.request import Request, urlopen
import time
import xml.sax
import cv2
import numpy as np
from matplotlib import pyplot as plt

headers2 = {}

if __name__ == "__main__":

    headers = {
        'Accept': 'application/xml'
    }

    headers2 = {
    }

    while 1:
        request = Request('https://s3-eu-west-1.amazonaws.com/helvar-stream/thermaldata.png',
                          headers=headers)
        response = urlopen(request)
        cur = response.read()
        with open("D:\\thermaldata.png", "wb") as fp:
            fp.write(cur)

        img = cv2.imread("D:\\thermaldata.png")
        img = cv2.copyMakeBorder(img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        thr = 170

        img = cv2.medianBlur(img, 3)
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print("thr: " + str(thr))
        ret, img3 = cv2.threshold(img2, thr, 255, cv2.THRESH_BINARY)
        # img = cv2.imread('star.jpg', 0)
        print(img.shape)
        print(img3.shape)
        height, width = img3.shape

        im2, contours, hierarchy = cv2.findContours(img3, 1, 2)
        maxSquare = 0
        maxIndex = 0
        for i in range(len(contours)):
            cnt = contours[i]
            s = cv2.contourArea(cnt)
            if (s > maxSquare):
                maxSquare = s
                maxIndex = i
        print("i:", maxIndex)
        cnt = contours[maxIndex]
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)
        ratio = w / h
        ratio_threshold = 1
        if ratio < ratio_threshold:
            try:
                request = Request('http://10.100.0.74/human-existence-input/1', headers=headers2)
                response_body = urlopen(request).read()
                print(response_body)
            except:
                print("Cannot connect.")
        else:
            try:
                request = Request('http://10.100.0.74/human-existence-input/0', headers=headers2)
                response_body = urlopen(request).read()
                print(response_body)
            except:
                print("Cannot connect.")
        time.sleep(10)
