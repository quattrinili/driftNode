import os # APIs for paths and running terminal commands
import shutil # file copy tools
import sys # for reading commandline arguments and exit
import yaml # loading and writing of yaml files

import datetime # time to string
import time # sleep and time to string

import socket # Socket APIs

import picamera # raspicam APIs
from picamera.array import PiRGBArray
import cv2 # OpenCV APIs

import rospy # ROS APIs
from cv_bridge import CvBridge, CvBridgeError # conversion from OpenCV to ROS
from sensor_msgs.msg import CameraInfo, Image, CompressedImage # ROS messages
import camera_info_manager # service for the camera calibration

class raspicamera:
    """The raspicamera class
    
    Some utilities for setting the raspicamera and publish ROS messages.
    
    """
    
    def __init__(self, image_width=640, image_height=480, fps=10, 
                shutter_speed=0,
                iso=0,
                eps=0.1,
                timeout=30,
                save_dir="~/ros_catkin_ws/src/Nodes/raspicam/calibrations/",
                parameters_file_name="camera-parameters",
                parameters_file_format="yaml",
                date_format="%Y-%m-%d-%H-%M-%S",
                backup=True):
        # Initialization of the camera
        self.camera = picamera.PiCamera()
        self.camera.resolution = (image_width, image_height)
        self.camera.framerate = fps
        self.shutter_speed = shutter_speed
        if shutter_speed > 0:
          self.camera.shutter_speed = self.shutter_speed
        self.iso = iso
        if iso > 0:
            self.camera.iso = self.iso
        self.eps = eps
        self.timeout = timeout
        
        self.save_dir = save_dir
        self.parameters_file_name = parameters_file_name
        self.parameters_file_format = parameters_file_format
        self.date_format = date_format
        self.backup = backup
        
        self.stream = picamera.array.PiRGBArray(self.camera)
        
        # Allow the camera to warmup
        time.sleep(0.1)
        
    def set_manual_mode(self):
        self.camera.saturation = self.camera.saturation
        self.camera.sharpness = self.camera.sharpness
        self.camera.contrast = self.camera.contrast
        self.camera.brightness = self.camera.brightness
        if self.iso == 0:
            self.camera.iso = self.camera.iso
        else:
            self.camera.iso = iso
        g = self.camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g
        if self.shutter_speed == 0:
            self.camera.shutter_speed = self.camera.exposure_speed
        else:
            self.camera.shutter_speed = self.shutter_speed
        self.camera.exposure_mode = 'off'
        self.camera.exposure_compensation = self.camera.exposure_compensation
    
    def set_auto_mode(self):
        self.camera.exposure_mode = 'auto'
        self.camera.awb_mode = 'auto'  
    
    def print_camera_parameters(self):
       print self.camera.digital_gain
       print self.camera.analog_gain
       print self.camera.awb_gains
       print self.camera.shutter_speed
    
    def load_camera_parameters(self, camera_parameters_file):
        if os.path.exists(camera_parameters_file): # Redundant check
            # TODO handling of errors in the opening
            with open(camera_parameters_file, 'r') as input_file:
               self.stream.truncate()
               camera_parameters = yaml.load(input_file)
               start = time.time()
               while (float(abs(self.camera.digital_gain - camera_parameters['digital_gain'])) > self.eps or float(abs(self.camera.analog_gain - camera_parameters['analog_gain'])) > self.eps) and time.time() - start < self.timeout:
                   self.stream.seek(0)
                   self.camera.capture(self.stream, format="bgr", use_video_port=True, resize=(640,480))

               self.camera.saturation = camera_parameters['saturation']
               self.camera.sharpness = camera_parameters['sharpness']
               self.camera.constrast = camera_parameters['contrast']
               self.camera.brightness = camera_parameters['brightness']
               self.camera.iso = camera_parameters['iso']
               self.camera.awb_mode = 'off'
               self.camera.awb_gains = camera_parameters['awb_gains']
               self.camera.shutter_speed = camera_parameters['shutter_speed']
               self.camera.exposure_compensation = camera_parameters['exposure_compensation']
               self.camera.exposure_mode = 'off'
            if self.backup:

                output_file = os.path.join(self.save_dir, 
                        ''.join([self.parameters_file_name, os.extsep, 
                              self.parameters_file_format]))
                if camera_parameters_file != output_file:
                    # From <parameters_filename>_<date> to <parameters_filename>
                    shutil.copy(camera_parameters_file, 
                      os.path.join(self.save_dir, 
                            ''.join([self.parameters_file_name, os.extsep, 
                                  self.parameters_file_format])))
                else:
                    # From <parameters_filename> to <parameters_filename>_<date>
                    timestr = time.strftime(self.date_format)
                    shutil.copy(camera_parameters_file, 
                    os.path.join(self.save_dir, 
                            ''.join([self.parameters_file_name, '_', 
                                    timestr, os.extsep, 
                                    self.parameters_file_format])))
            return True
        else:
            return False
     
        
    def save_camera_parameters(self):
        camera_parameters_file = os.path.join(self.save_dir, 
                                        ''.join([self.parameters_file_name, 
                                                os.extsep, 
                                                self.parameters_file_format]))
        # TODO handling of errors in the opening
        with open(camera_parameters_file, 'w') as output_file:
            data = dict(
               saturation = self.camera.saturation,
               sharpness = self.camera.sharpness,
               contrast = self.camera.contrast,
               brightness = self.camera.brightness,
               iso = self.camera.iso,
               awb_gains = self.camera.awb_gains,
               shutter_speed = self.camera.shutter_speed,
               exposure_compensation = self.camera.exposure_compensation,
               digital_gain = self.camera.digital_gain,
               analog_gain = self.camera.analog_gain
            )
            output_file.write(yaml.dump(data, default_flow_style=True))
        if self.backup:
            # From <parameters_filename> to <parameters_filename>_<date>
            timestr = time.strftime(self.date_format)
            shutil.copy(camera_parameters_file, 
                os.path.join(self.save_dir, 
                        ''.join([self.parameters_file_name, '_', 
                                timestr, os.extsep, 
                                self.parameters_file_format])))


