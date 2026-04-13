# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

OmniSpatialAI is a multi-module research/educational repository covering Spatial AI topics: SLAM, Computer Vision, Control Systems, GIS, Path Planning, and ROS robotics. It is **not** a single unified application — each subdirectory is an independent project with its own build system.

## Build Commands

### Standalone C++ Modules (SLAM, Planning)

Each C++ module (e.g., `slam/visual_odometry/`, `slam/mapping/`, `slam/visual_vocabulary/dbow_demos/`, `planning/mapping/`) builds independently:

```bash
cd <module_dir>
mkdir build && cd build
cmake ..
make -j$(nproc)
```

Key external dependencies vary by module:
- `slam/visual_odometry/`: OpenCV 3, Eigen3, Sophus, Ceres, G2O, Pangolin, CSparse
- `slam/visual_vocabulary/dbow_demos/`: OpenCV 4, DBoW2 or DBoW3 (controlled by `-DWITH_DBOW2=ON/OFF` and `-DWITH_DBOW3=ON/OFF`). Third-party libs are resolved via the `$CG_THIRDPARTY` environment variable.
- `planning/mapping/`: OpenCV

### ROS Packages

All packages under `ros/` must be built inside a catkin workspace:

```bash
cd <your_catkin_ws>
catkin_make --source /opt/user_data/code/OmniSpatialAI/ros/
```

Required ROS packages include `ros-noetic-xacro`, `ros-noetic-robot-state-publisher`, and others listed in each `package.xml`.

### GIS Python Scripts

```bash
pip install folium numpy matplotlib
python gis/folium_csv.py  # or folium_kml.py
```

### Documentation (MkDocs)

```bash
pip install mkdocs-material
mkdocs serve        # local preview at http://127.0.0.1:8000
mkdocs build        # outputs to site/
```

## Architecture

### Module Layout

- **`slam/visual_odometry/`** — C++ implementations of feature-based and direct pose estimation methods. The top-level `CMakeLists.txt` coordinates three sub-modules: `visual_tracking/` (optical flow), `ba_gauss_newton/` (bundle adjustment via Gauss-Newton, Ceres, and G2O), and `mono_vo/` (monocular VO pipeline). A shared `pose_estimation` library is built and linked across executables.
- **`slam/mapping/`** — Dense/semi-dense mapping using RGBD data and OctoMap. Includes RViz/launch files for visualization.
- **`slam/visual_vocabulary/dbow_demos/`** — Loop closure detection using DBoW2/DBoW3. Build variant is selected at CMake configure time.
- **`slam/slam_frameworks/`** — ROS launch files for external SLAM frameworks (RTAB-Map, etc.).
- **`slam/scripts/`** — Standalone Python scripts for probabilistic algorithms (EKF-SLAM, Monte Carlo, GMM, Brownian motion) and data visualization.
- **`slam/slam_dataset/tum/`** — TUM RGB-D dataset utilities. The header `tum_data_rgbd.h` is auto-downloaded by CMake if absent.
- **`planning/mapping/`** — C++ path cross-point computation using OpenCV. Source files live in `src/`.
- **`ros/`** — Independent catkin packages: `cgbot/` (robot URDF/Xacro + Gazebo), `robot1_description/`, `sensors_test/`, `joy_ctrl/`, `movebase_demo/`, `rosbag_rw/`, `using_map/`, `simple_layers/`, `actionlib_tutorials/`.
- **`control_system/`** — MATLAB/Simulink `.m` files for transfer functions and step response analysis.
- **`gis/`** — Python scripts using Folium for geographic visualization (CSV/KML data on interactive maps).
- **`docs/`** — MkDocs source (Markdown). Navigation is defined in `mkdocs.yml`. The `site/` directory contains the built static site (do not edit manually).

### Conventions

- C++ standard: C++11 minimum for most modules; C++17 required for `dbow_demos` (uses `std::filesystem`).
- CMake pattern: `find_package` → `include_directories` → `target_link_libraries`. Custom `cmake_modules/` finders (FindG2O, FindCSparse) are present in `slam/visual_odometry/cmake_modules/`.
- ROS packages use standard structure: `package.xml`, `CMakeLists.txt`, `launch/`, `urdf/`/`xacro/`.
- Documentation: new modules go in `docs/` and must be registered in `mkdocs.yml` under the appropriate nav section.
