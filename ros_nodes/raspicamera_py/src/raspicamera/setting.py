import socket
import numpy
import time
import cv2
import gflags
import sys

gflags.DEFINE_string("ip_address", "127.0.0.1", "IP address")
gflags.DEFINE_integer("port", 5001, "Port number")

try:
  sys.argv = gflags.FLAGS(sys.argv)  # parse flags
except gflags.FlagsError, e:
  print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
  sys.exit(1)

TCP_IP = gflags.FLAGS.ip_address
TCP_PORT = gflags.FLAGS.port

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connected = False
while not connected:
  try:
    sock.connect((TCP_IP, TCP_PORT))
    connected = True
  except:
    print "not yet available"
    time.sleep(1)


print "Connected" 
s=""

state = 0 # 0: not set yet, 1: checking, 2: DONE

while state !=2:
    
    #sock.sendto("CONNECT", (UDP_IP, UDP_PORT))
   
    print "waiting for data"

    #data, addr = sock.recvfrom(46080)
    data = sock.recv(46080)
    print "data received"

    s += data
    print len(s)
    if len(s) == (46080*20):

        frame = numpy.fromstring (s,dtype=numpy.uint8)
        frame = frame.reshape (480,640,3)

        cv2.imshow('frame',frame)
        cv2.waitKey(1000/30)

        s=""
        if state == 0:
          answer = ''
          while answer != 'y' and answer != 'n': 
            answer = raw_input('Accept the setting of the image? (y/n)')
            print answer
          print "sending answer"
          sock.send(answer)
          if answer == 'y':
            state = 1
        elif state == 1:
          answer = ''
          while answer != 'y' and answer != 'n' and answer != 'r': 
            answer = raw_input('Continue checking (y/n) or reset (r)?')
            print answer
            sock.send(answer)
            if answer == 'n':
              state = 2
            elif answer == 'r':
              state = 0


    
sock.close()
