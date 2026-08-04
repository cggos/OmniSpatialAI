# Repository Guidelines

## Project Structure & Module Organization

OmniSpatialAI is a collection of independent Spatial AI projects, not a single application. Core algorithms live in `slam/` (visual odometry, mapping, and vocabulary demos) and `navigation/` (planning and control). ROS packages are split between `ws_ros1/src/` and `ws_ros2/src/`. Python utilities and data-processing tools are under `scripts/` and `gis/`; MATLAB/Simulink examples are under `navigation/control_system/`. The Qt/OpenCV desktop application is in `sai_studio/`. Documentation source belongs in `docs/`, with navigation configured in `mkdocs.yml`. Keep generated `build/`, `install/`, `log/`, and `site/` directories out of source changes.

## Build, Test, and Development Commands

Build each standalone C++ module from its own directory:

```bash
cmake -S slam/visual_odometry -B build/visual_odometry
cmake --build build/visual_odometry -j
```

For ROS 2, run `colcon build --packages-select sai_tb3_sim` from `ws_ros2/`, then source `install/setup.bash`. Build ROS 1 packages from `ws_ros1/` with `catkin_make`. Use `pytest scripts/test` for repository Python lint tests. Preview documentation with `mkdocs serve`; validate the static build with `mkdocs build`.

Dependencies vary by module (for example OpenCV, Eigen, Sophus, Ceres, ROS, or Qt), so check the nearest `README.md`, `CMakeLists.txt`, and `package.xml` before building.

## Coding Style & Naming Conventions

Use four spaces in Python and follow PEP 8; prefer `snake_case` for modules, functions, and variables. C++ code should follow the surrounding module, use descriptive `snake_case` filenames, and retain the module’s configured C++ standard (C++11 through C++17). Format C/C++ sources with `scripts/code/batch_format.sh` or the repository `.clang-format` when present. ROS package names, launch files, topics, and parameters use lowercase `snake_case`. Add new documentation pages to the appropriate `mkdocs.yml` navigation section.

## Testing Guidelines

Place Python tests in `scripts/test/` or beside the owning module as `test_*.py`. ROS 2 lint tests use `pytest` markers such as `linter` and require the relevant `ament_*` packages. For CMake modules that register tests, run `ctest --test-dir <build-dir> --output-on-failure`. There is no repository-wide coverage threshold; add focused regression tests for changed behavior and document any hardware, dataset, or simulator prerequisites.

## Commit & Pull Request Guidelines

Recent history uses short Conventional Commit subjects such as `feat: add sai_studio`, `refactor: ws_ros1`, and `docs: update sai_nav/README.md`. Use an imperative subject with a suitable prefix (`feat:`, `fix:`, `refactor:`, `docs:`, or `test:`), and keep each commit scoped to one module. Pull requests should describe the affected module, motivation, commands run, and required dependencies. Link related issues and include screenshots or recordings for Qt, RViz, Gazebo, map, or documentation changes.
