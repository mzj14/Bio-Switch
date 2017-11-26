from urllib.request import Request, urlopen
import time
import xml.sax
import cv2

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

        print("shape: ", img.shape)
        height, width, channel = img.shape
        print("h: "+str(height)+", w: "+str(width))
        print("channel 1: "+str(channel))

        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print("channel 2: " + str(img2.shape))
        # cv2.namedWindow("ffffffff")
        # cv2.imshow("ffffffff", img)

        sum = 0
        num = height * width
        for i in range(height):
            for j in range(width):
                sum += img2[i, j]
                # img2[i, j] = (255 - img[i, j])  # For GRAY_SCALE image ;
                # img2[i,j] = (255-img[i, j][0], 255-img[i, j][1], 255-img[i, j][2])
        avg = sum / num
        if avg > 30:
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
        print("sum: "+str(sum)+", avg: "+str(avg))

        time.sleep(10)

