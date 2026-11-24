#!/bin/bash
sudo apt-get update && sudo apt-get install -y bluez
sudo apt install ros-humble-rviz2
sudo rm /etc/apt/sources.list.d/ros2.sources
curl 'https://raw.githubusercontent.com/Interbotix/interbotix_ros_manipulators/main/interbotix_ros_xsarms/install/amd64/xsarm_amd64_install.sh' > xsarm_amd64_install.sh
chmod +x xsarm_amd64_install.sh
./xsarm_amd64_install.sh -d humble
source $HOME/.bashrc
