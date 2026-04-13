# OmniSpatialAI

**All-in-One Spatial AI**

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen)](https://osai.cgabc.xyz/)

OmniSpatialAI is a comprehensive repository dedicated to the field of Spatial AI, integrating Simultaneous Localization and Mapping (SLAM), Computer Vision, Control Systems, Geographic Information Systems (GIS), and Robotics (ROS).

---

## 🚀 Key Modules

- **[Control System](./control_system/):** MATLAB/Simulink implementations for digital signal processing and control theory.
- **[SLAM](./slam/):** Advanced algorithms for Visual Odometry, Mapping, and Loop Closure, with benchmark datasets.
- **[GIS](./gis/):** Geographic data visualization and processing using Python and Folium.
- **[Planning](./planning/):** Path planning and mapping algorithms implemented in C++.
- **[ROS](./ros/):** Robot models (URDF/Xacro), sensor simulations (Gazebo), and actionlib tutorials.
- **[XR & Metaverse](./docs/XR/):** Documentation and frameworks for AR/VR applications and tracking.

## 🛠 Tech Stack

- **Languages:** C++ (11/14/17), Python 3, MATLAB/Simulink.
- **Frameworks:** ROS (Noetic/Melodic), MkDocs.
- **C++ Libraries:** OpenCV, Eigen3, Sophus, Ceres, G2O, Pangolin.
- **Python Libraries:** Folium, NumPy, Matplotlib.

## 📁 Directory Structure

```text
OmniSpatialAI/
├── control_system/     # Control theory & DSP (MATLAB)
│   └── basics/         # Transfer function & step response scripts
├── gis/                # Geographic Information Systems (Python)
├── planning/           # Path planning & Mapping (C++)
├── ros/                # ROS packages, URDFs, Gazebo simulations
│   └── extras/         # Non-catkin utilities (ros_matlab, ros_video, scripts)
├── slam/               # Visual Odometry, Mapping, SLAM frameworks
├── docs/               # Project documentation (MkDocs source)
└── mkdocs.yml          # Documentation configuration
```

## 📖 Documentation

The full documentation is available at **[sai.cgabc.xyz](https://sai.cgabc.xyz/)**.

To run documentation locally:
```bash
pip install mkdocs-material
mkdocs serve
```

## 🏗 Getting Started

### C++ Modules
```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### ROS
Ensure you are in a `catkin` workspace:
```bash
catkin_make --source <path_to_omnispatialai>/ros/
```

## 📜 License

This project is licensed under the [BSD 3-Clause License](LICENSE).
