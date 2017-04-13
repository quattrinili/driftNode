cmake_minimum_required(VERSION 2.8.3)
project(raspicamera_py)

find_package(catkin REQUIRED COMPONENTS rospy sensor_msgs)
include_directories(include ${catkin_INCLUDE_DIRS})
find_package(OpenCV REQUIRED)

catkin_python_setup()
catkin_package(CATKIN_DEPENDS sensor_msgs)

