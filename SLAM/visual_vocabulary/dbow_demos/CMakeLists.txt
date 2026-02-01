cmake_minimum_required(VERSION 3.5)
project(visual_vocabulary)

set(CMAKE_BUILD_TYPE "Release")
# Use a modern C++ standard for std::filesystem
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_FLAGS "-O3 -g")

option(WITH_DBOW2 "use DBoW2" ON)
option(WITH_DBOW3 "use DBoW3" OFF)

set(PLATFORM_ARCH "x86-64")

set(OpenCV_DIR "$ENV{CG_THIRDPARTY}/${PLATFORM_ARCH}/opencv/lib/cmake/opencv4/")
find_package(OpenCV 4 REQUIRED)
list(APPEND LIBS ${OpenCV_LIBS})
include_directories(${OpenCV_INCLUDE_DIRS})

# Some older libstdc++ implementations require linking against stdc++fs
find_library(STDCXXFS_LIB stdc++fs)
if(STDCXXFS_LIB)
  list(APPEND LIBS ${STDCXXFS_LIB})
endif()

if(WITH_DBOW2)
  add_definitions(-DWITH_DBOW2)
  # find_package(DBoW2 REQUIRED)
  set(DBoW2_DIR "$ENV{CG_THIRDPARTY}/${PLATFORM_ARCH}/dbow2/lib/cmake/DBoW2")
  set(DBOW2_INCLUDE_DIRS "$ENV{CG_THIRDPARTY}/${PLATFORM_ARCH}/dbow2/include")
  set(DBOW2_LIBRARY_DIRS "$ENV{CG_THIRDPARTY}/${PLATFORM_ARCH}/dbow2/lib")
  set(DBOW2_LIBRARIES DBoW2)
  include_directories(${DBOW2_INCLUDE_DIRS})
  link_directories(${DBOW2_LIBRARY_DIRS})
  list(APPEND LIBS ${DBOW2_LIBRARIES})

  add_executable(demo_dbow2 demo_dbow2.cpp)
  target_link_libraries(demo_dbow2 ${LIBS})
endif()
if(WITH_DBOW3)
  add_definitions(-DWITH_DBOW3)
  set(DBoW3_INCLUDE_DIRS "/usr/local/include")
  set(DBoW3_LIBS "/usr/local/lib/libDBoW3.so")
  list(APPEND LIBS ${DBoW3_LIBS})
endif()

add_executable(create_voc create_voc.cpp)
target_link_libraries(create_voc ${LIBS})

add_executable(loop_closure loop_closure.cpp)
target_link_libraries(loop_closure ${LIBS})
