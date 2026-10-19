from setuptools import find_packages
from setuptools import setup

setup(
    name='surgical_interfaces',
    version='0.1.0',
    packages=find_packages(
        include=('surgical_interfaces', 'surgical_interfaces.*')),
)
