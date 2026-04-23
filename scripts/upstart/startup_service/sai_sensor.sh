#!/usr/bin/env bash

source /opt/ros/noetic/setup.bash
source /home/jetson/projects/sai_app-20240220/app/ros1/devel/setup.bash

# export ROS_MASTER_URI=http://192.168.55.1:11311
# export ROS_IP=192.168.55.1

export ROS_MASTER_URI=http://nano1.local:11311
export ROS_IP=nano1.local

rosclean purge -y
sleep 1
roslaunch sai_ros1 camera.launch

exit 0
