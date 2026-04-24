#!/usr/bin/env python3
"""Main simulation launch: TurtleBot3 in a Gazebo world.

Equivalent to: ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
but with world and robot loaded via separate sub-launches so either can be
swapped independently at the command line.

Usage examples:
  # Default (burger robot, standard turtlebot3 world)
  ros2 launch sai_tb3_sim sim.launch.py

  # Swap robot model
  ros2 launch sai_tb3_sim sim.launch.py robot_model:=waffle

  # Use a different world
  ros2 launch sai_tb3_sim sim.launch.py world:=/path/to/my.world

  # Both world and robot overridden
  ros2 launch sai_tb3_sim sim.launch.py robot_model:=waffle_pi world:=/path/to/my.world

  # Extend Gazebo startup wait time on slow machines (default: 5s)
  ros2 launch sai_tb3_sim sim.launch.py gazebo_wait:=10.0
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def launch_setup(context, *args, **kwargs):
    robot_model = LaunchConfiguration('robot_model').perform(context)
    world = LaunchConfiguration('world').perform(context)
    x_pose = LaunchConfiguration('x_pose').perform(context)
    y_pose = LaunchConfiguration('y_pose').perform(context)
    z_pose = LaunchConfiguration('z_pose').perform(context)
    gazebo_wait = float(LaunchConfiguration('gazebo_wait').perform(context))

    launch_dir = os.path.join(
        get_package_share_directory('sai_tb3_sim'), 'launch'
    )

    # --- 场景：立即启动 ---
    world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, 'world.launch.py')
        ),
        launch_arguments={'world': world}.items(),
    )

    # --- 机器人：延迟启动，等待 gzserver 就绪 ---
    # gzserver 启动并完成世界加载需要一定时间。spawn_entity.py 内置了
    # -timeout 60 兜底（最长等 60 秒服务可用），但过早发起请求会让
    # spawn_entity.py 处于"等待服务"状态，终端无输出，看起来像卡住。
    # gazebo_wait 提供一段冷启动缓冲，让 Gazebo 在 spawn 前完成初始化。
    robot_launch = TimerAction(
        period=gazebo_wait,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(launch_dir, 'robot.launch.py')
                ),
                launch_arguments={
                    'robot_model': robot_model,
                    'use_sim_time': 'true',
                    'x_pose': x_pose,
                    'y_pose': y_pose,
                    'z_pose': z_pose,
                }.items(),
            )
        ],
    )

    return [world_launch, robot_launch]


def generate_launch_description():
    pkg_this = get_package_share_directory('sai_tb3_sim')
    default_world = os.path.join(pkg_this, 'worlds', 'turtlebot3_world.world')

    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_model',
            default_value='burger',
            description='TurtleBot3 model to spawn: burger | waffle | waffle_pi'
        ),
        DeclareLaunchArgument(
            'world',
            default_value=default_world,
            description='Full path to Gazebo world file (.world or .model)'
        ),
        DeclareLaunchArgument(
            'gazebo_wait',
            default_value='5.0',
            description='Seconds to wait for gzserver to be ready before spawning the robot'
        ),
        DeclareLaunchArgument(
            'x_pose', default_value='-2.0',
            description='Initial X position of the robot'
        ),
        DeclareLaunchArgument(
            'y_pose', default_value='-0.5',
            description='Initial Y position of the robot'
        ),
        DeclareLaunchArgument(
            'z_pose', default_value='0.01',
            description='Initial Z position of the robot'
        ),

        OpaqueFunction(function=launch_setup),
    ])
