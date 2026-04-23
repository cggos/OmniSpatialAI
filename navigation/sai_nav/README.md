# SAI Navigation

---

- [ ] Follow Object
- [ ] Follow Waypoint
- [ ] Follow Path
- [ ] Obstacle Avoidance

# Prerequisites

```shell
sudo apt install ros-$ROS_DISTRO-gazebo-ros-pkgs \
  ros-$ROS_DISTRO-navigation2 \
  ros-$ROS_DISTRO-nav2-bringup \
  ros-$ROS_DISTRO-slam-toolbox \
  ros-$ROS_DISTRO-xacro \
  ros-$ROS_DISTRO-robot-localization \
  ros-$ROS_DISTRO-rmw-cyclonedds-cpp
```

# Mapping

## Prepare Environment

### Simulate Environment

for Turtlebot3

```bash
# sudo vim /opt/ros/foxy/share/turtlebot3_navigation2/param/burger.yaml


export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# or
ros2 launch gazebo_ros gazebo.launch.py world:=/opt/ros/foxy/share/turtlebot3_gazebo/worlds/turtlebot3_houses/burger.model
```

Custom World

```shell
ros2 launch sai_nav sim_empty_world.launch.py # or sim_tb3_world.launch.py
```

### Real Environment

#### Sensing

```shell
git clone https://github.com/Slamtec/rplidar_ros.git -b ros2

ros2 launch rplidar_ros view_rplidar_a1_launch.py
```

## Run SLAM

```bash
ros2 launch slam_toolbox online_async_launch.py []use_sim_time:=True]

# or if use turtlebot3
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

## Move Robot

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

for Turtlebot3

```shell
ros2 run turtlebot3_teleop teleop_keyboard
# or
ros2 run turtlebot3_gazebo turtlebot3_drive
```

## Save Grid Map

```bash
ros2 run nav2_map_server map_saver_cli -f $CG_DM_ROOT/xxx/gazebo_grid_map
```

# Navigation with Map

Start Gazebo world if use sim environment

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Run Navigation

```bash
ros2 launch sai_nav nav2.launch.py [params_file:=xxx.yaml]
```

for Turtlebot3

```shell
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=true map:=<grid_map.yaml>
```

- 2D Pose Estimation
- Nav2 Goal
