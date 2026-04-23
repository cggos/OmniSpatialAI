#!/usr/bin/env bash

export ROS_MASTER_URI=http://jet01.local:11311
export ROS_IP=jet01.local

source /home/jetson/projects/algorithm/sai_vod/app/ros1/devel/setup.bash

rosclean purge -y
sleep 2

roslaunch sai_ros1 run_all.launch &
