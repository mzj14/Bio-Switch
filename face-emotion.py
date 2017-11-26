# coding:utf-8
import cv2
import sys
import time
import json
import http.client, urllib.request, urllib.parse, urllib.error, base64
from urllib.request import Request, urlopen
headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '*****'
}
headers2 = {
}
params = urllib.parse.urlencode({
})

rule = {'disgust':0,'sadness':1,'neutral':2,'happiness':3,'fear':4,'contempt':5,'surprise':6,'anger':7,'noFace':-1}

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)
cap.set(1, 10.0)
c = 1


while True:
    ret,frame = cap.read()
    if ret == True:
        frame = cv2.flip(frame, 1)
        #cv2.imshow("frame", frame)
        cv2.imwrite('face/'+str(c) + '.jpg',frame) 
        body = open(r'face/'+str(c)+'.jpg', mode='rb')
        c+=1

        try:
            conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
            conn.request("POST", "/emotion/v1.0/recognize?%s" % params, body, headers)
            response = conn.getresponse()
            data = response.read()
            jsonRes = json.loads(data.decode())
            lenRes = len(jsonRes)
            code = -1
            for j in jsonRes:
                if type(j) == type({}):
                    if 'scores' in j:
                        scores = j['scores']
                        maxRes = max(scores, key=lambda key: scores[key])
                        code = rule[maxRes]
                    else:
                        continue
                else:
                    continue
            if(code != rule['noFace'] and code != rule['anger'] and code != rule['sadness']):
                code = rule['neutral']
            print(code)

            try:
                request = Request('http://10.100.0.74//human-face-input/'+str(code), headers=headers2)
                response_body = urlopen(request).read()
                print(response_body)
            except:
                print('Cannot connect')

            print(data)
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
    time.sleep(1)
cap.release()
cv2.destroyAllWindows()

