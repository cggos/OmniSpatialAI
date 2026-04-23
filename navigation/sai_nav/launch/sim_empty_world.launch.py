import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_name = 'sai_nav'
    pkg_share = get_package_share_directory(pkg_name)

    # 启动 Gazebo Server 和 Client
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
    )

    # 机器人状态发布节点 (RSP)
    robot_name = 'diy_robot'
    xacro_file = os.path.join(pkg_share, 'urdf', f'{robot_name}.urdf.xacro')
    robot_description_config = Command(['xacro', ' ', xacro_file])
    # doc = xacro.process_file(xacro_file)
    # robot_description_config = doc.toxml()

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        # parameters=[{'robot_description': robot_description_config}],
        parameters=[{'robot_description': ParameterValue(robot_description_config, value_type=str)}],
        arguments=['--ros-args', '--log-level', 'info']
    )

    # 在 Gazebo 中生成机器人
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', robot_name],  # same to robot name in urdf/xacro
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        node_robot_state_publisher,
        spawn_entity
    ])
