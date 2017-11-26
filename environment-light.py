# coding:utf-8
import cv2
import sys
import time
import json
import http.client, urllib.request, urllib.parse, urllib.error, base64
from urllib.request import Request, urlopen
import numpy

headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Content-Length':0
}

headers2 = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)
cap.set(1, 10.0)

c = 1
para = 32768

paraM = [[0.49,0.31,0.2],[0.17697,0.8124,0.01063],[0,0.01,0.99]]
divider = 0.17697
threshold = 0.5
gap = 0.25

def RGB2XYZ(mb,mg,mr):
    mX = (0.49*mr+0.31*mg+0.2*mb)/divider
    mY = (0.17697*mr+0.8124*mg+0.01063*mb)/divider
    mZ = (0*mr+0.01*mg+0.99*mb)/divider
    msum = mX+mY+mZ
    mx = mX/msum
    my = mY/msum
    return mx,my

def compare(mx,my,cx,cy):
    isSet = False
    if(cx < 0 or cy < 0): return False,0,0
    ax = cx
    ay = cy
    if(mx-cx>threshold):
        ax = cx-gap
    if(my-cy>threshold):
        ay = cy-gap
    if(cx-mx>threshold):
        ax = cx+gap
    if(cy-my>threshold):
        ay = cy+gap
    if(ax != cx or ay != cy):isSet = True
    if(ax > 1): ax = 1
    if(ax < 0):ax = 0
    if(ay > 1): ay = 1
    if(ay < 0):ay = 0
    return isSet,ax,ay



while True:
    ret,frame = cap.read()
    if ret == True:
        frame = cv2.flip(frame, 1)
        #cv2.imshow("frame"+str(c), frame)
        (B,G,R) = cv2.split(frame)
        mb = numpy.mean(B)
        mg = numpy.mean(G)
        mr = numpy.mean(R)
        mx,my = RGB2XYZ(mb,mg,mr)

        request = Request('https://5nk8a0rfn5.execute-api.eu-west-1.amazonaws.com/v1/dali-data?start='+str(0)+'&limit='+str(1)+'&end='+str(9)+'', headers=headers)
        response_body = urlopen(request).read()
        #print(response_body)
        jsonRes = json.loads(response_body.decode())

        currentId = -1
        currentx = -1
        currenty = -1
        currentIn = -1
        for j in jsonRes:
            if type(j) == type({}):
                if 'device' in j:
                    currentId = j['device']
                    currentx = j['nQuery_X']/para
                    currenty = j['nQuery_Y']/para
                    currentIn = j['nBrightness']
                else:
                    continue
            else:
                continue
        isSet,ax,ay = compare(mx,my,currentx,currenty)
        print("Actual Color",mx,my)
        print("Last Set Color",currentx,currenty)
        if(isSet == True):
            print('Color To Change',ax,ay)
            request2 = Request('https://5nk8a0rfn5.execute-api.eu-west-1.amazonaws.com/v1/command?device='+str(int(currentId))+'&level='+str(int(currentIn))+'&colour_x='+str(int(ax*para))+'&colour_y='+str(int(ay*para))+'', headers=headers2)
            response_body2 = urlopen(request2).read()
            #print(response_body2)
        else:
           print('Not Have To Change') 
        print('**************************************') 

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
    time.sleep(1)
    c+=1
cap.release()
cv2.destroyAllWindows()

