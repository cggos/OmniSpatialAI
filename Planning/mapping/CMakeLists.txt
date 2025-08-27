cmake_minimum_required(VERSION 3.10)
project(map)

find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

include_directories(include)

add_executable(test_cross_points src/test_cross_points.cpp src/paths_cross_points.cpp)
target_link_libraries(test_cross_points ${OpenCV_LIBS})

add_executable(test_with_simulation src/test_with_simulation.cpp src/paths_cross_points.cpp)
target_link_libraries(test_with_simulation ${OpenCV_LIBS})
