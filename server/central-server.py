#!/usr/bin/env python

# Team: THS
# Name: Zijun Ma
# Function: This is an exmaple of HTTPServer running on the Bio-Switch central controller

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen
from time import sleep

import regression_tree as regTrees
import matplotlib.pyplot as plt
from numpy import *

import os
import json

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# urls for restful api
request_url_1 = "https://5nk8a0rfn5.execute-api.eu-west-1.amazonaws.com/v1/command?device={device_id}&level={level_id}&colour_x={colour_x_id}&colour_y={colour_y_id}"
request_url_2 = "https://5nk8a0rfn5.execute-api.eu-west-1.amazonaws.com/v1/dali-data"

# model tree to predict color_x
Tree1 = {}
# model tree to predict color_y
Tree2 = {}
# model tree to predict brightness_level
Tree3 = {}

# normal mm number
self_mm = 40
# normal facial expression
self_face = 2
# example warm color
self_warm_color_x = 22759
self_warm_color_y = 8101
# example cool color
self_cool_color_x = 5458
self_cool_color_y = 290
# color for day light
self_color_x = 10922
self_color_y = 10922
# brightness_level
self_brightness_level = 100
self_human_existence = False
# luminaire id
self_device_id = 0

'''
def get_light_color(device_id):
    request = Request(request_url_2, headers=headers)
    response = urlopen(request).read()
    response_jsons = json.loads(response.decode('utf-8'))
    print("response_jsons = ", response_jsons)
    colour_x = 30000
    colour_y = 30000
    brightness_level = 100
    for response_json in response_jsons:
        if response_json["nDali_Address"] == 0.0:
            colour_x, colour_y, brightness_level = response_json['nQuery_X'], response_json['nQuery_Y'], response_json['nActual_Level']
            print("get_light_color, response", colour_x, colour_y, brightness_level, flush=True)
            break;
    return colour_x, colour_y, brightness_level
'''

def set_light_color(device_id, colour_x_id, colour_y_id, level_id):
    global self_device_id
    global self_color_x
    global self_color_y
    global self_brightness_level

    request_url_real = request_url_1.format(device_id = device_id, level_id = level_id, colour_x_id = colour_x_id, colour_y_id = colour_y_id)
    request = Request(request_url_real, headers=headers)
    response = urlopen(request).read()
    self_device_id, self_brightness_level, self_color_x, self_color_y = device_id, level_id, colour_x_id, colour_y_id

    print("set_light_color, response", response, flush=True)

class LightSwitchHTTPRequestHandler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        print('the server address is', self.client_address);
        print('the string of the request is', self.requestline);
        print('the path of the request is', self.path);
        if 'human-existence-input' in self.path:
            self.handle_existence_input()
        elif 'voice-input' in self.path:
            self.handle_voice_input()
        elif 'human-face-input' in self.path:
            self.handle_face_input()
        elif 'ring-input' in self.path:
            self.handle_ring_input()
        else:
            self.send_text_response(200, "Error request url!")
        return

    # handle existence input
    def handle_existence_input(self):
        global self_human_existence
        global self_device_id

        if 'human-existence-input/0' in self.path:
            # no people, turn off the light
            self.send_text_response(200, "no human exist.")
            if self_human_existence:
                set_light_color(self_device_id, 0, 0, 0)
                self_human_existence = False
        else:
            # people exists, turn on the light
            self.send_text_response(200, "human exist.")
            if not self_human_existence:
                set_light_color(self_device_id, 10922, 10922, 100)
                self_human_existence = True
        return

    # handle face expression input
    def handle_face_input(self):
        global self_face
        global self_mm
        global self_device_id

        if 'human-face-input/1' in self.path:
            self.send_text_response(200, 'response sadness')
            self_face = 1
        elif 'human-face-input/2' in self.path:
            self.send_text_response(200, 'response neutral')
            self_face = 2
        elif 'human-face-input/7' in self.path:
            self.send_text_response(200, 'response anger')
            self_face = 7
        elif 'human-face-input/-1' in self.path:
            self.send_text_response(200, 'response no face')
        else:
            self.send_text_response(200, 'error get requst')

        global Tree_1
        global Tree_2

        # make prediction of the ideal light condition
        color_x = regTrees.treeForeCast(Tree_1, [self_face, self_mm])
        color_y = regTrees.treeForeCast(Tree_2, [self_face, self_mm])
        brightness_level = regTrees.treeForeCast(Tree_3, [self_face, self_mm])
        set_light_color(self_device_id, int(color_x), int(color_y), int(brightness_level))

    # handle voice input
    def handle_voice_input(self):
        global self_device_id
        global self_color_x
        global self_color_y
        global self_brightness_level
        global self_warm_color_x
        global self_warm_color_y
        global self_cool_color_x
        global self_cool_color_y

        if 'voice-input/0' in self.path:
            self.send_text_response(200, 'make it warmer')
            if self_color_x <= 10922:
                # current light is cold or middle
                set_light_color(self_device_id, self_warm_color_x, self_warm_color_y, self_brightness_level)
            else:
                # current color is already warm color
                set_light_color(self_device_id, self_color_x + 100, self_color_y, self_brightness_level)

            # set_light_color(0, int(color_x), int(color_y), int(brightness_level + 30))
        elif 'voice-input/1' in self.path:
            self.send_text_response(200, 'make it cooler')
            # print('voice-input/1, self_color_x', self_color_x)
            # print('voice-input/1, self_color_y', self_color_y)
            if self_color_x >= 10922:
                # current light is warm or middle
                set_light_color(self_device_id, self_cool_color_x, self_cool_color_y, self_brightness_level)
            else:
                # current color is already warm color
                set_light_color(self_device_id, self_color_x - 100, self_color_y - 100, self_brightness_level)

        elif 'voice-input/2' in self.path:
            self.send_text_response(200, 'make it brighter')
            set_light_color(self_device_id, self_color_x, self_color_y, self_brightness_level + 30)
        elif 'voice-input/3' in self.path:
            self.send_text_response(200, 'make it darker')
            set_light_color(self_device_id, self_color_x, self_color_y, self_brightness_level - 30)
        else:
            self.send_text_response(200, 'not known')

    # handle ring input
    def handle_ring_input(self):
        global self_mm
        global Tree_1
        global Tree_2
        global Tree_3
        global self_face
        self_mm = int(self.path[12:])
        color_x = regTrees.treeForeCast(Tree_1, [self_face, self_mm])
        color_y = regTrees.treeForeCast(Tree_2, [self_face, self_mm])
        brightness_level = regTrees.treeForeCast(Tree_3, [self_face, self_mm])
        self.send_text_response(200, 'ring input is ' + str(self_mm))
        set_light_color(self_device_id, int(color_x), int(color_y), int(brightness_level))

    # send text response with status code
    def send_text_response(self, status_code, content):
        # Send response status code
        self.send_response(status_code)

        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()

        # Send message back to client
        message = content

        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

    # send json response with status code
    def send_json_response(self, status_code, content):
        # Send response status code
        self.send_response(status_code)

        # Send headers
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        # Send message back to client
        message = content

        # Write content as utf-8 data
        self.wfile.write(bytes(json.dumps(message), "utf8"))
        return

def getModelTreeFromFile(file_name):
    myDat = regTrees.loadDataSet(file_name)
    myMat = mat(myDat)
    model_tree = regTrees.createTree(myMat)
    return model_tree

def run():
    # get the model tree
    # model tree for color x
    global Tree_1
    global Tree_2
    global Tree_3

    Tree_1 = getModelTreeFromFile('train_data/train_regression_color_x.txt')
    Tree_2 = getModelTreeFromFile('train_data/train_regression_color_y.txt')
    Tree_3 = getModelTreeFromFile('train_data/train_regression_brightness_level.txt')

    print('http server is starting...')

    #ip and port of server
    #by default http server port is 80
    server_address = ('10.100.0.74', 80)
    httpd = HTTPServer(server_address, LightSwitchHTTPRequestHandler)

    print('http server is running...')

    httpd.serve_forever()

if __name__ == '__main__':
    run()
