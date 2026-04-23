# sudo apt install ros-melodic-robot-upstart

# install
rosrun robot_upstart install --master "http://127.0.0.1:11311" --setup `pwd`/devel/setup.bash sai_ros1/launch/run_all.launch --logdir /tmp/
# start
sudo systemctl daemon-reload && sudo systemctl start vod

# uninstall
rosrun robot_upstart uninstall mytest
# stop
sudo systemctl stop vod
