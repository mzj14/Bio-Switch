# Bio-Switch: Toward an Intelligent In-door Light Control Solution

### Authors: Zijun Ma , Yinuo Yang, and Zhiqing Zhang

## ABSTRACT
We hereby propose Bio-Switch, which comprehensively collects and analyzes human emotional and physical data to determine the appropriate in-door light condition, as an intelligent light control solution. Bio-Switch 1) automatically learns the appropriate light condition from the detected human emotional data as well as basic psychology knowledge, 2) creates user-friendly interface by allowing human voice as user input, and 3) changes the light condition based on simple human action.

## SYSTEM DESIGN

### Overall Architecture

* A color camera is deployed to detect human facial expression while a smart ring is used to sense human stress level, together profiling human emotion.

* A voice sensor is deployed to collect human voice as input for controlling light condition.

* A infrared camera is deployed to detect human existence and simple human action.  

* A central controller is deployed in the room to process the continuous data stream sent from the above sensors and change the light condition through DALI controller's REST APIs.

![](report/4)

### Features and Implementation

#### Feature 1

Bio-Switch is able to turn on/off the light automatically based on the existence of people.

#### Device/Service
Infrared camera

#### Implementation
* Obtain the thermal image from the API ```https://s3-eu-west-1.amazonaws.com/helvar-stream/thermaldata.png```

* Convert the thermal image into Grey Level Image

* Calculate the average value of the grey level, and set a threshold to detect if there are people in the room. (In our experiment, threshold is set to 30.)

* Send an HTTP request to our server, indicating whether there is human in the room or not.

* The central controller sends command to turn on/off the light according to the existence of people via the REST APIs. If there is no one in the room for 5 min, the light will be turned off. If there is someone in the room, light will be turned on.

#### Feature 2
Bio-Switch is able to change the light condition according to the mental state of people.

#### Device/Service
Color camera, Smart rings & Microsoft Azure Facial Recognition Service

#### Implementation

* We use the MM value obtained from the API of the Moodmetric ring, which descripts the user's current emotional intensity. Low MM numbers can be achieved at a calm and quiet environment, while high MM numbers are typical when angry, stressed or when in intensive social situations.

* We implemented an application on Android Platform to connect the ring and android smart phone (Android 6.0). The smart phone collects data of MM value on real time and sends the data to our server through HTTP requests.

* We obtain the expressions of people through API of Emotion Sensing in Microsoft Azure Cloud Service Platform. We detect the image of face with the laptop the user are using on real time, and then we detect the expressions of the user, including sad, angry and neutral, with emotion sensing API. We also send this emotion information to the server.

* The controller has a general mapping between emotion data (i.e., facial expression and MM number) and the light condition (i.e., color_x, color_y and the brightness level) in advanced, which is learned from sensor data mining (e.g., CART algorithm). Later, the controller decides the appropriate light condition according to the map.

* The server sends command to modify the light intensity and light color according to the result we obtain via the REST APIs.

#### Feature 3
Bio-Switch is able to accept user speech as input to change the light condition on personal will.

#### Device/Service
Voice Sensor(Microphone) & Microsoft Azure Speech Recognition Service

#### Implementation
* We continuously evaluate the noise of the environment so that when the Microphone attains the speech of people, it is able to ignore the environmental noise.

* We use the APIs provided by Microsoft Azure Speech Recognition Service, for a real-time convertion from speech to text.

* The voice commands include:    
  + ```'Make it warmer.'```  
  + ```'Make it cooler.'```
  + ```'Make it brighter.'```
  + ```'Make it darker.'```

* We send the text command to our server. The server deals with the command as the followings,
  + For ```'Make it warmer.'```, we increase color_x by 100
  + For ```'Make it cooler.'```, we decrease color_x by 100 and color_y by 100
  + For ```'Make it brighter.'```, we increase the light intensity by 30
  + For ```'Make it darker.'```, we decrease the light intensity by 30

* The server sends command to modify the light intensity and light color according to the result we obtain via the REST APIs.

* Please be noted that using human speech as input is quite a scalable choice. It is easy to implement multiple command approach by recognizing different speeches.

#### Feature 4

Bio-Switch is able to change the light condition according to the action of people.

#### Device/Library

Infrared camera & OpenCV 

#### Implementation

* Obtain the thermal image from the API ```https://s3-eu-west-1.amazonaws.com/helvar-stream/thermaldata.png```

* Convert the thermal image into Binary Image

* Detect the counter of human body and infer the actual position(i.e., lying, standing, sitting)

* Send an HTTP request to our server, indicating whether the person is lying in the room or not.

* The central controller sends command to turn up/down the light according to the existence of people via the REST APIs. If the person in the room has laid down for 30 seconds, the light will be turned down. If the person in the room has sit down or stood up for 30 seconds in the room, the light will be turned on.

#### Feature 5
Bio-Switch is able to fine-tune the light condition according to the environment.

#### Device
Color camera

#### Implementation
* We detect the actual color in RGB space with the camera of the laptop. We catch the image on real time with the laptop camera, split it into R,G and B channels, calculate the average value in these channels, and convert it into CIE color space.

![](report/formula.png)

![](report/cie2.png)
(https://en.wikipedia.org/wiki/CIE_1931_color_space)

* We obtain the last record of light conditions setting through the API ```/v1/dali-data```.

* On each axis, if the difference is larger than a threshold, which currently we set to 0.5, it means the environmental light is strong, and directly setting the luminaire components' light could not guarantee the appropriate light condition in the room. Therefore, on this axis we strengthen the light color to get an appropriate blended effect with the environmental light.

* The server sends command to modify the light color according to the result we obtain via the REST APIs.

* This feature could be considered as a further adjustment for light condition setting in Feature 2.
