# OmniSpatialAI

**All-in-One Spatial AI**

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen)](https://osai.cgabc.xyz/)

OmniSpatialAI is a comprehensive repository dedicated to the field of Spatial AI, integrating Simultaneous Localization and Mapping (SLAM), Computer Vision, Control Systems, Geographic Information Systems (GIS), and Robotics (ROS).

---

## 🚀 Key Modules

- **[Control System](./ControlSystem/):** MATLAB/Simulink implementations for digital signal processing and control theory.
- **[SLAM](./SLAM/):** Advanced algorithms for Visual Odometry, Mapping, and Loop Closure, with benchmark datasets.
- **[GIS](./GIS/):** Geographic data visualization and processing using Python and Folium.
- **[Planning](./Planning/):** Path planning and mapping algorithms implemented in C++.
- **[ROS](./ROS/):** Robot models (URDF/Xacro), sensor simulations (Gazebo), and actionlib tutorials.
- **[XR & Metaverse](./docs/XR/):** Documentation and frameworks for AR/VR applications and tracking.

## 🛠 Tech Stack

- **Languages:** C++ (11/14/17), Python 3, MATLAB/Simulink.
- **Frameworks:** ROS (Noetic/Melodic), MkDocs.
- **C++ Libraries:** OpenCV, Eigen3, Sophus, Ceres, G2O, Pangolin.
- **Python Libraries:** Folium, NumPy, Matplotlib.

## 📁 Directory Structure

```text
OmniSpatialAI/
├── ControlSystem/      # Control theory & DSP (MATLAB)
├── GIS/                # Geographic Information Systems (Python)
├── Planning/           # Path planning & Mapping (C++)
├── ROS/                # ROS packages, URDFs, Gazebo simulations
├── SLAM/               # Visual Odometry, Mapping, SLAM frameworks
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
catkin_make --source <path_to_omnispatialai>/ROS/
```

## 📜 License

This project is licensed under the [BSD 3-Clause License](LICENSE).
