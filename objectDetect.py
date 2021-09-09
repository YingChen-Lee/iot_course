######## Webcam Object Detection Using Tensorflow-trained Classifier #########
#
# This code is based off the TensorFlow Lite image classification example at:
# Author: Evan Juras
# https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/TFLite_detection_webcam.py

import os
import cv2
import numpy as np
import sys
import time
from tflite_runtime.interpreter import Interpreter
from threading import Thread

GRAPH_NAME = 'detect.tflite'
LABELMAP_NAME = 'labelmap.txt'

default_threshold = 0.7
imW, imH = 1280, 720
#imW, imH = 640, 480
customized_threshold = {'stop sign':0.2, 'person':0.5}

flip = -1 #0 means flipping around the x-axis, and positive value means flipping around y-axis. Negaive value means flipping around both axis 

CWD_PATH = os.getcwd()
PATH_TO_CKPT = os.path.join(CWD_PATH, GRAPH_NAME)
PATH_TO_LABELS = os.path.join(CWD_PATH, LABELMAP_NAME)

# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class VideoStream():
    # camera object that controls video streaming from the picamera
    def __init__(self, resolution=(640,480), framerate = 30):
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3, resolution[0])
        ret = self.stream.set(4, resolution[1])

        (self.grabbed, self.frame) = self.stream.read()
        
        self.stopped = False

    def start(self):
        Thread(target = self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

class ObjectDetector():
    def __init__(self):
        with open(PATH_TO_LABELS, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]
        # Have to do a weird fix for label map if using the COCO "starter model" from
        # https://www.tensorflow.org/lite/models/object_detection/overview
        # First label is '???', which has to be removed.
        if self.labels[0] == '???':
            del(self.labels[0])

        self.interpreter = Interpreter(model_path=PATH_TO_CKPT)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]

        self.is_floating_model = (self.input_details[0]['dtype'] == np.float32)
        self.input_mean = 127.5
        self.input_std = 127.5

        self.freq = cv2.getTickFrequency()

        self.videostream = VideoStream(resolution=(imW,imH), framerate=30).start()
        time.sleep(1)

    def get_objects_framerate(self):
        # start timer for calculating framerate
        t1 = cv2.getTickCount()
        
        frame1 = self.videostream.read()
        
        frame = cv2.flip(frame1, -1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (self.width, self.height))
        input_data = np.expand_dims(frame_resized, axis=0)

        if self.is_floating_model:
            input_data = (np.float32(input_data) - self.input_mean) / self.input_std

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0] # class index of detected objects
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]

        detected_objects = []
        for i in range(len(scores)):
            obj = self.labels[int(classes[i])]
            if obj in customized_threshold:
                if (customized_threshold[obj] <= scores[i] <= 1.0):
                    detected_objects.append( (obj, scores[i]) )
            else:
                if default_threshold <= scores[i]:
                    detected_objects.append( (obj, scores[i]) )
                #detected_objects.append( (self.labels[int(classes[i])], scores[i]) )

        t2 = cv2.getTickCount()
        time1 = (t2 - t1) / self.freq
        frame_rate_calc = 1/time1
        return detected_objects, frame_rate_calc

    def stop_camera(self):
        self.videostream.stop()

if __name__ == '__main__':
    ob = ObjectDetector()
    while True:
        objects, framerate = ob.get_objects_framerate()
        print(objects)
        print(framerate)
