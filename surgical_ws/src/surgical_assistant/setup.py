from glob import glob

from setuptools import find_packages, setup

package_name = 'surgical_assistant'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tesis',
    maintainer_email='iandre.cabrera@gmail.com',
    description='Asistente robotico quirurgico (voz + vision + MoveIt 2).',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'voice_command_node = surgical_assistant.voice_command_node:main',
            'instrument_detection_node = surgical_assistant.instrument_detection_node:main',
            'hand_tracking_node = surgical_assistant.hand_tracking_node:main',
            'task_coordinator_node = surgical_assistant.task_coordinator_node:main',
        ],
    },
)
