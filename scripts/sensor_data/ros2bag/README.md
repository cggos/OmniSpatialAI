# ros2bag_py

---

# Install

## for ROS Humble

```bash
sudo apt install ros-humble-rosbag2-py
```

## for ROS Foxy

```bash
mkdir -p ~/ws_rosbag2/src

cd ~/ws_rosbag2/src
git clone -b foxy-future https://github.com/ros2/rosbag2.git

cd ~/ws_rosbag2
colcon build --packages-up-to rosbag2_py --merge-install

# verify
source ~/ws_rosbag2/install/setup.zsh
```

## Test

```bash
python3 -c "import rosbag2_py; print(rosbag2_py.__version__)"
# or
python3 -c "import rosbag2_py; print(dir(rosbag2_py))"
```
