# OmniSpatialAI - All-in-One Spatial AI

This repository is a comprehensive collection of tools, algorithms, and documentation for Spatial AI, covering Simultaneous Localization and Mapping (SLAM), Computer Vision (CV), Control Systems, Geographic Information Systems (GIS), Robot Operating System (ROS), Autonomous Driving, and Extended Reality (XR).

## Project Overview

- **Control System**: MATLAB/Simulink-based control theory and signal processing.
- **SLAM**: C++ and Python implementations of Visual Odometry, Mapping, Loop Closure, and Benchmarking.
- **GIS**: Python-based geographic data processing and visualization using tools like Folium.
- **Planning**: C++ modules for path planning and mapping.
- **ROS**: A collection of ROS packages for robot description, sensors, and simulation.
- **XR & Metaverse**: Documentation and resources for AR SDKs and applications.
- **Documentation**: Managed via MkDocs (Material theme), available at `https://osai.cgabc.xyz/`.

## Main Technologies

- **Languages**: C++ (11/14), Python 3, MATLAB/Simulink.
- **Libraries**:
    - **C++**: OpenCV, Eigen3, Sophus, Ceres, G2O, Pangolin, CSparse.
    - **Python**: Folium, NumPy, Matplotlib.
- **Middleware**: ROS (Noetic/Melodic).
- **Build Systems**: CMake, Catkin.

## Building and Running

### Standalone C++ Modules (SLAM, Planning)
Most C++ components use standard CMake.

```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### ROS Packages
ROS components should be built within a catkin workspace.

```bash
# Example for a workspace structure where ros/ is the source directory
cd <your_catkin_ws>
catkin_make --source /opt/user_data/code/OmniSpatialAI/ros/
```
Note: Ensure ROS dependencies are installed (e.g., `ros-noetic-xacro`, `ros-noetic-robot-state-publisher`).

### GIS Python Scripts
Python scripts often require `folium`.

```bash
pip install folium
# Or via conda
conda install -c conda-forge folium
```

### Documentation
To serve the documentation locally:

```bash
pip install mkdocs-material
mkdocs serve
```

## Development Conventions

- **C++**:
    - Use C++11 or higher.
    - Follow standard CMake practices (`find_package`, `include_directories`, `target_link_libraries`).
    - Keep source files in `src/` and headers in `include/`.
- **ROS**:
    - Follow standard ROS package structure (`package.xml`, `CMakeLists.txt`, `launch/`, `urdf/`).
    - Use `xacro` for robot descriptions.
- **Documentation**:
    - All new features or modules should be documented in the `docs/` directory and added to `mkdocs.yml`.
    - Use Markdown for documentation.
- **Python**:
    - Follow PEP 8 guidelines.
    - Document dependencies (e.g., in comments or a `requirements.txt` if applicable).
