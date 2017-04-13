#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix
import socket #to read hostname
import os #to join ROS_NAMESPACE
import serial
import struct

DRIFTER_NUMBERS = 6

def callback(data):
    rospy.loginfo(rospy.get_caller_id()+" I heard [lat: %f long: %f alt: %f time: %s]", 
	data.latitude, data.longitude, data.altitude, data.header.stamp)
    
def gps_listener():

    ser = serial.Serial(
             port='/dev/ttyUSB0',
             baudrate = 9600,
             parity=serial.PARITY_NONE,
             stopbits=serial.STOPBITS_ONE,
             bytesize=serial.EIGHTBITS,
             #timeout=1
             )
    counter=0

    rospy.init_node('gps_listener', anonymous=True)
    gps_publishers = []
    for i in range(DRIFTER_NUMBERS):
        gps_publishers.append(rospy.Publisher(os.path.join("dn" + str(i+1),'gps_chatter'), NavSatFix, queue_size=10))
    rospy.Subscriber(os.path.join(socket.gethostname(), "gps_chatter"), NavSatFix, callback)
    r = rospy.Rate(10) # 10hz
  
    while not rospy.is_shutdown():
        print "waiting"
        x = ser.read(12) # TODO constant.
        if len(x) == 12:
            # TODO time? now assumed that more or less the transmission is instantaneous.
            drifter_id, latitude, longitude = struct.unpack("Bff", x)

            gps_msg = NavSatFix()
  
            #gps_msg.header.stamp = gps_time_unix
            gps_msg.header.stamp = rospy.get_rostime()
            gps_msg.header.frame_id = os.path.join("dn" + str(drifter_id) , "gps_link")
                              
            gps_msg.latitude = latitude
            gps_msg.longitude = longitude
            print gps_msg
            gps_publishers[drifter_id-1].publish(gps_msg)
        else:
            print "no message"
        #r.sleep()
if __name__ == '__main__':
    gps_listener()
