#!/usr/bin/env python

#********WoooHooo!!! Imports!!********#
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix  #added gps_time string to the NavSatFix message until driftNode message package is complete
from gps import *
import gps
import numpy
import sys, os, subprocess
import calendar
from datetime import datetime
import socket #to get hostname

# TODO library for radio.
import serial
import struct
import time
#***********End 'O Imports************#

RADIO_PUBLISH_DEFAULT = True
TIME_INTERVAL = 30 # seconds between ping to the base station.


seq = 0
NODE_FREQUENCY = 10  #ros looping frequency


gpsd = None  #instantiating gpsd
gpsd = gps.gps("localhost", "2947")  #gpsd is broadcasting to default tcp port 2497
gpsd.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)  #gpsd stuff

def gps_talker():
    gps_pub = rospy.Publisher('gps_chatter', NavSatFix, queue_size=10)  #instantiating publisher
    rospy.init_node('gps_talker', anonymous=False)  #initializing node

    radio_publish = rospy.get_param('radio_publish', RADIO_PUBLISH_DEFAULT) # Frequency to read sensor.

    ser = None
    if radio_publish:
        # TODO default variables parameter.
        ser = serial.Serial(
           port='/dev/ttyUSB0',
           baudrate = 9600,
           parity=serial.PARITY_NONE,
           stopbits=serial.STOPBITS_ONE,
           bytesize=serial.EIGHTBITS,
           timeout=1
           )
    # get hostname.
    drifter_id = int(filter(str.isdigit, socket.gethostname()))    
    counter_time = rospy.get_rostime()
    time_interval = rospy.Duration(TIME_INTERVAL + drifter_id * 2)

    gps_link = os.path.join(socket.gethostname(), "gps_link")

    global NODE_FREQUENCY
    r = rospy.Rate(NODE_FREQUENCY) # 10hz
  
    while not rospy.is_shutdown():
        try:  #making sure gpsd isn't being obtuse
            report = gpsd.next()
            #print report
            #print gpsd.fix.track
            #print " "
            #print gpsd.satellites
            #if not numpy.isnan(gpsd.fix.altitude):

            if not numpy.isnan(gpsd.fix.track):

                global seq
                
                current_time = rospy.get_rostime()

                gps_msg = NavSatFix()  #instantiating gps message                                      
                gps_msg.header.seq = seq
                      
                gps_msg.header.stamp = current_time
                gps_msg.header.frame_id = gps_link
                                  
                gps_msg.latitude = gpsd.fix.latitude
                gps_msg.longitude = gpsd.fix.longitude
                gps_msg.altitude = gpsd.fix.altitude
              
                gps_pub.publish(gps_msg)  #publish ros gps message
                #if seq%50 == 0:  #not printing all lines so we don't swamp the terminal
                  #rospy.loginfo("[lat: %f long: %f alt: %f time: %i:%i]", 
                    #gps_msg.latitude, gps_msg.longitude, gps_msg.altitude, gps_msg.header.stamp.secs, gps_msg.header.stamp.nsecs)

                if radio_publish and current_time - counter_time > time_interval:
                    data = struct.pack("Bff", drifter_id, gps_msg.latitude, 
                        gps_msg.longitude)
                    x=ser.write(data)
                    if x < 12:
                        rospy.logerr("Exception when sending GPS data.")
                    else:
                        counter_time = current_time
                      
                seq +=1
            else:
                #rospy.logwarn("GPSD is being obtuse.  Probably just no GPS fix yet.")
                pass
          
        except Exception:  #yup, gpsd is being obtuse
            rospy.logerr("Exception when reading GPSD data.")

        r.sleep()  #wait until next time to run
        
if __name__ == '__main__':
    try:
        gps_talker()
    except rospy.ROSInterruptException: 
        rospy.logerr("main except")
        pass
