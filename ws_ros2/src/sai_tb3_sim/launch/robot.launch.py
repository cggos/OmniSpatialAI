#!/usr/bin/env python3
"""Load a TurtleBot3 robot model into a running Gazebo simulation.

Starts robot_state_publisher (for TF) and spawns the robot via Gazebo's
native model database (-database mode), which is equivalent to the
<include><uri>model://turtlebot3_burger</uri></include> in a world file.

Using -database instead of -file / -topic avoids two problems:
  1. -file / -topic send the URDF string to Gazebo, which cannot resolve
     package:// mesh URIs → Gazebo physics engine hangs and freezes the GUI.
  2. -topic mode spins in a tight loop printing repeated log lines while
     waiting for the robot_description topic → terminal floods / appears stuck.

Supported robot_model values: burger | waffle | waffle_pi
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    robot_model = LaunchConfiguration('robot_model').perform(context)
    use_sim_time = LaunchConfiguration('use_sim_time').perform(context)
    x_pose = LaunchConfiguration('x_pose').perform(context)
    y_pose = LaunchConfiguration('y_pose').perform(context)
    z_pose = LaunchConfiguration('z_pose').perform(context)

    urdf_path = os.path.join(
        get_package_share_directory('turtlebot3_description'),
        'urdf',
        f'turtlebot3_{robot_model}.urdf'
    )

    if not os.path.isfile(urdf_path):
        raise FileNotFoundError(
            f"URDF not found for robot_model='{robot_model}': {urdf_path}\n"
            "Valid values: burger, waffle, waffle_pi"
        )

    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    # robot_state_publisher 负责发布 TF 树，URDF 通过 robot_description 参数传入
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time == 'true',
            'robot_description': robot_description,
        }],
    )

    # 通过 Gazebo 模型数据库加载机器人，等价于 world 文件中的：
    #   <include><uri>model://turtlebot3_burger</uri></include>
    # 使用原生 SDF 模型，Gazebo 可直接找到网格路径，不会因 package:// 卡住。
    # -timeout：等待 /spawn_entity 服务可用的最长秒数。
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', f'turtlebot3_{robot_model}',
            '-database', f'turtlebot3_{robot_model}',
            '-timeout', '60',
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
        ],
    )

    return [robot_state_publisher, spawn_entity]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_model',
            default_value='burger',
            description='TurtleBot3 model: burger | waffle | waffle_pi'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Gazebo simulation clock'
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
