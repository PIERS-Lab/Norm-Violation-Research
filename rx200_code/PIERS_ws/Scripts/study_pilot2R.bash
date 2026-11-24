echo "Demo Configuration 2(Right)!"
echo "Verbose1"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d33
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r33
wait

echo "Ceasar"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d12
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r12
wait

echo "Base1"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d13
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r13
wait

echo "Binary (Task Appropriation)"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d31
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r31
wait

echo "Misorder"
read -p "Press anything to begin"
ros2 launch nvr_arm_control deliver.launch.py config:=d22
wait   
read -p "Press anything to return"
ros2 launch nvr_arm_control deliver.launch.py config:=r22
wait
