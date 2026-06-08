# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a ROS (Robot Operating System) simulation workspace for an MIT-style racecar based on [mit-racecar](https://github.com/mit-racecar). It targets ROS Melodic/Noetic on Ubuntu with Gazebo simulation. The workspace root is `ws_racecar/`; this repo lives at `ws_racecar/src/racecar/`.

## Build

Install dependencies (run from workspace root `ws_racecar/`):
```sh
rosdep install --from-paths src --ignore-src --rosdistro $ROS_DISTRO -y
```

Build the workspace (run from workspace root):
```sh
catkin build -DCMAKE_BUILD_TYPE=Release
```

Source the workspace after building:
```sh
source ws_racecar/devel/setup.bash
```

## Running the Simulation

**Mapping** (two terminals):
```sh
roslaunch racecar_gazebo racecar.launch world_name:=racecar_runway
roslaunch racecar_gazebo slam_gmapping.launch
rosrun map_server map_saver -f map_runway
```

**Navigation** — Terminal 1 is always `racecar.launch`; Terminal 2 selects the localization mode:

| Terminal 2 launch file | Localization source | Notes |
|---|---|---|
| `racecar_navigation_gz.launch` | Gazebo ground truth (`map→base_link`) | Fast debug, not realistic |
| `racecar_navigation_amcl_gz.launch` | AMCL + Gazebo odometry (`odom→base_link`) | Realistic TF chain |
| `racecar_navigation_amcl_lo.launch` | AMCL + laser odometry (`laser_scan_matcher`) | Closest to real deployment |

```sh
# Terminal 1
roslaunch racecar_gazebo racecar.launch world_name:=racecar_runway
# Terminal 2 (pick one above)
roslaunch racecar_gazebo racecar_navigation_amcl_gz.launch map_name:=map_runway
# Terminal 3
rosrun racecar_gazebo path_pursuit.py
```

`path_pursuit.py` subscribes to `/pf/pose/odom` for robot position. For `_gz` modes this is relayed from `/vesc/odom` (Gazebo world coordinates). For `_lo` mode it comes from `map_pose_publisher.py` which looks up `map→base_link` TF — necessary because `laser_scan_matcher` starts its odom frame at (0,0) rather than world coordinates.

Other world variants: `world_name:=racecar_cg`, and launch files `racecar_normal_runway.launch`, `racecar_parking_1.launch`, `racecar_tunnel.launch`, `racecar_walker.launch`, `racecar_ar.launch`.

## Package Architecture

The repo has three main packages and a `system/` directory of vendored dependencies:

### `racecar_description`
URDF/xacro robot model. The robot is defined in `urdf/racecar.xacro` using macros from `urdf/macros.xacro`. Gazebo plugins (diff drive, camera, laser) are in `urdf/racecar.gazebo`. 3D meshes (.dae/.STL) and Gazebo world models (track environments, AR markers, cones) live under `meshes/` and `models/`.

### `racecar_control`
ros_control configuration bridging Ackermann commands to joint controllers. `config/racecar_control.yaml` sets PID gains for four wheel velocity controllers and two steering hinge position controllers. `scripts/servo_commands.py` subscribes to `/racecar/ackermann_cmd_mux/output` (AckermannDriveStamped) and re-publishes to individual wheel/steering joint topics; speed is scaled by ×40 to convert m/s to rad/s for the 0.05 m radius wheel.

### `racecar_gazebo`
Primary simulation package. Contains:
- **`launch/`** — world-specific launch files and `slam_gmapping.launch` / `racecar_rviz.launch`
- **`worlds/`** — Gazebo `.world` files for each track scenario
- **`map/`** — pre-built occupancy grid maps (`.pgm` + `.yaml`) for `map_runway` and `map_tunnel`
- **`config/`** — Navigation stack params: AMCL, costmaps (common/global/local), TEB local planner, RViz configs
- **`scripts/`** — Python nodes (see below)
- **`src/`** — C++ node (`findLine.cpp`, image-based line following)
- **`model/`** — Gazebo traffic light models (`green_light`, `red_light`)

Key Python scripts in `racecar_gazebo/scripts/`:
| Script | Purpose |
|---|---|
| `path_pursuit.py` | Pure pursuit controller; subscribes to `/pf/pose/odom` + TEB global plan, publishes to navigation Ackermann mux |
| `global_hybrid_A_star.py` | Hybrid A* planner using local costmap; alternative path planner |
| `findLine.py` | Camera-based yellow line follower using OpenCV HSV thresholding |
| `gazebo_odometry.py` | Publishes `map→base_link` TF + `/vesc/odom` from Gazebo ground truth (used by `racecar_navigation_gz.launch`) |
| `gazebo_odometry_odom.py` | Same as above but publishes `odom→base_link` TF; AMCL provides `map→odom` (used by `racecar_navigation_amcl_gz.launch`) |
| `map_pose_publisher.py` | Looks up `map→base_link` TF and republishes as Odometry on `/pf/pose/odom`; needed for laser-odom mode because `laser_scan_matcher` starts its odom at (0,0) |
| `keyboard_teleop.py` | Keyboard teleoperation node |
| `light_contrl.py` | Traffic light state machine controller |

### `system/`
Vendored third-party ROS packages:
- `ackermann_msgs` — AckermannDrive/AckermannDriveStamped message types
- `joystick_drivers/joy` — Joystick input node
- `vesc/` — VESC motor controller driver, Ackermann↔VESC conversion, odometry
- `racecar/` — Top-level racecar bringup; `ackermann_cmd_mux` priority multiplexer for combining navigation/teleop commands
- `hokuyo_node` — Hokuyo LiDAR driver
- `serial` — Serial communication library
- `waypoint_logger` — Records waypoints to CSV

## Key ROS Topic Flow

```
Teleop/Nav input
    → /vesc/low_level/ackermann_cmd_mux/input/{teleop,navigation}
    → ackermann_cmd_mux (priority multiplexer)
    → /racecar/ackermann_cmd_mux/output
    → servo_commands.py
    → /racecar/{left,right}_{rear,front}_wheel_velocity_controller/command
    → /racecar/{left,right}_steering_hinge_position_controller/command
```

Localization (`_gz` modes): `/vesc/odom` relayed to `/pf/pose/odom`. Localization (`_lo` mode): `map_pose_publisher.py` looks up `map→base_link` TF from AMCL + `laser_scan_matcher` chain and publishes as `/pf/pose/odom`.

## Camera Integration (darknet_ros)

To use YOLO object detection, update the camera topic in darknet_ros's `ros.yaml`:
```yaml
subscribers:
  camera_reading:
    topic: /camera/zed/rgb/image_rect_color
```
Then: `roslaunch darknet_ros darknet_ros.launch`
