"""Lanza los 4 nodos del asistente quirúrgico.

Ejemplo:
    ros2 launch surgical_assistant surgical_assistant.launch.py \
        model_path:=/home/usuario/models/instrumental_obb.onnx dry_run:=true
(La cámara RGB-D, el driver xarm_ros2 y MoveIt 2 se lanzan aparte.)
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = get_package_share_directory('surgical_assistant')
    default_params = os.path.join(share, 'config', 'params.yaml')

    params_file = LaunchConfiguration('params_file')
    model_path = LaunchConfiguration('model_path')
    setfit_dir = LaunchConfiguration('setfit_model_dir')
    dry_run = ParameterValue(LaunchConfiguration('dry_run'), value_type=bool)

    return LaunchDescription([
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('model_path', default_value='',
                              description='Modelo YOLO-OBB exportado a .onnx'),
        DeclareLaunchArgument('setfit_model_dir', default_value='',
                              description='Directorio del modelo SetFit (vacío = reglas)'),
        DeclareLaunchArgument('dry_run', default_value='true',
                              description='true = el coordinador no envía movimientos'),

        Node(package='surgical_assistant', executable='voice_command_node',
             name='voice_command_node', output='screen',
             parameters=[params_file, {'setfit_model_dir': setfit_dir}]),
        Node(package='surgical_assistant', executable='instrument_detection_node',
             name='instrument_detection_node', output='screen',
             parameters=[params_file, {'model_path': model_path}]),
        Node(package='surgical_assistant', executable='hand_tracking_node',
             name='hand_tracking_node', output='screen',
             parameters=[params_file]),
        Node(package='surgical_assistant', executable='task_coordinator_node',
             name='task_coordinator_node', output='screen',
             parameters=[params_file, {'dry_run': dry_run}]),
    ])
