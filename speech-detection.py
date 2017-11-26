import speech_recognition as sr
import time
from urllib.request import Request, urlopen

headers = {
}

# obtain audio from the microphone

rule = {'Make it warmer.':0,'Make it cooler.':1,'Make it brighter.':2,'Make it darker.':3,'Not known':-1}
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Adapting...")
    r.adjust_for_ambient_noise(source, duration=5)
    print("Adaption Finished!")
while 1:
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
        BING_KEY = "*****"  # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
        code = -1
        try:
            strc = r.recognize_bing(audio, key=BING_KEY)
            print("Microsoft Bing Voice Recognition thinks you said " + strc)
            try:
                code = rule[strc]
            except:
                code = -1
            print(code)
            try:
                request = Request('http://10.100.0.74/voice-input/'+str(code), headers=headers)
                response_body = urlopen(request).read()
                print(response_body)
            except:
                print('Cannot connect')
            
        except sr.UnknownValueError:
            print("Microsoft Bing Voice Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))
    time.sleep(2)


