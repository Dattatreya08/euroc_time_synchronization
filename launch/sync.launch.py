from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='camera_player',
            executable='camera_player_node',
            name='camera_player',
            parameters=[{'dataset_path': '/root/docker_ws/datasets/euroc/MH_01_easy/MH_01_easy/mav0/cam0'}],
            output='screen'
        ),
        Node(
            package='imu_player',
            executable='imu_player_node',
            name='imu_player',
            parameters=[{'dataset_path': '/root/docker_ws/datasets/euroc/MH_01_easy/MH_01_easy/mav0/imu0'}],
            output='screen'
        ),
        Node(
            package='message_synchronizer',
            executable='synchronizer_node',
            name='message_synchronizer',
            output='screen'
        ),
    ])
