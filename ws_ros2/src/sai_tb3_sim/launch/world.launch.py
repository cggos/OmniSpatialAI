#!/usr/bin/env python3
"""Launch Gazebo server and client with a specified world file.

Decoupled from any robot model so the scene can be loaded independently.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_this = get_package_share_directory('sai_tb3_sim')

    # Pure scene without any embedded robot model.
    # The original turtlebot3_gazebo burger.model includes the robot via <include>,
    # so we use our own world file that contains only the environment geometry.
    default_world = os.path.join(pkg_this, 'worlds', 'turtlebot3_world.world')

    world = LaunchConfiguration('world')

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=default_world,
            description='Full path to the Gazebo world file (.world or .model)'
        ),
        DeclareLaunchArgument(
            'verbose',
            default_value='false',
            description='Set "true" to enable verbose Gazebo output'
        ),

        # Gazebo physics server
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
            ),
            launch_arguments={
                'world': world,
                'verbose': LaunchConfiguration('verbose'),
            }.items(),
        ),

        # Gazebo GUI client
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
            ),
        ),
    ])
